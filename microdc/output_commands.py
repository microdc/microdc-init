from microdc.template_parser import parsetemplate, readtemplate
from microdc.networking import generate_subnets


def setup_microdc_workarea(workdir, component_repos, datefile, overwrite=False):

    def create_root_folder(root_folder):
        print(("mkdir -p {}\n".format(root_folder)))

    def get_repos(repo_folder, repos):
        print(("mkdir -p {}\n".format(repo_folder)))
        for key, value in repos.items():
            if overwrite:
                print(("rm -rf {}/{}\n".format(repo_folder, key)))
            print(("[ -e {repo_folder}/{key} ] || \\\n"
                   "( git clone {value[git]} {repo_folder}/{key} && \\\n"
                   "  cd {repo_folder}/{key} && \\\n"
                   "  git checkout {value[ref]} )\n"
                   .format(key=key, value=value, repo_folder=repo_folder)))

    def stamp_setup_file(datefile):
        print(("date '+%d %b %Y %H:%M' > {}\n".format(datefile)))

    create_root_folder(workdir)
    get_repos("{}/repos".format(workdir), component_repos)
    stamp_setup_file(datefile)


def setup_environment(config, options):

    print(("export AWS_DEFAULT_REGION={region}\n"
           "export AWS_DEFAULT_PROFILE={profile}\n"
           "export AWS_PROFILE={profile}\n"
           .format(profile=config['accounts'][options.account]['awsprofile'],
                   region=config['accounts'][options.account]['region'])))
    return True


def run_kubectl(config, options):

    try:
        modules = config["kubectl_modules"]
    except KeyError:
        print("ERROR: No kubectl_modules specified in config yaml. "
              "These are required for kubectl to apply config on your k8s cluster")
        return

    if options.env not in list(config['accounts'][options.account]['environments'].keys()):
        raise ValueError("Env needs to be one of {}"
                         .format(list(config['accounts'][options.account]['environments'].keys())))

    acm_cert = config['accounts'][options.account]['sslcertificate']
    component_dir = "{workdir}/repos/{component}".format(workdir=options.workdir,
                                                         component='k8s-service-stack-full')
    environment = options.env
    domain = config['accounts'][options.account]['domain']

    print("\n".join(['export ENVIRONMENT_DOMAIN={environment}.{domain}',
                     'export LB_DNS_NAME=ingress.{environment}.{domain}',
                     'export INTERNAL_LB_DNS_NAME=ingress.internal.{environment}.{domain}',
                     'export ACM_CERT_ARN={acm_cert}\n'])
          .format(environment=environment,
                  domain=domain,
                  acm_cert=acm_cert))

    for module in modules:

        kubectl_apply_command = \
            'for file in $(find . -name "*.yaml"); do cat ${{file}} ' \
            '| envsubst | kubectl apply -f - ; done\n)' \
            if module.get("envsubst", False) else \
            'while true; do if kubectl apply -Rf .; then break; fi; done\n)'

        print("\n".join(['(\ncd {component_dir}/{module_name} && \\',
                         kubectl_apply_command,
                         ])
              .format(component_dir=component_dir, module_name=module["name"]))

    return True


def run_terraform(config, options):
    print("export TF_PLUGIN_CACHE_DIR=\"/tmp/terraform.d/plugin-cache\"")

    if options.action == "up":
        action = 'apply'
    elif options.action == "down":
        action = 'destroy -force'
    else:
        raise ValueError("{} is not supported".format(options.action))

    stacks = ['global', 'service', 'mgmt']
    if options.stack not in stacks:
        raise ValueError("Terraform stack needs to be on of {}".format(stacks))

    if not options.stack == 'global':
        if options.env not in list(config['accounts'][options.account]['environments'].keys()):
            raise ValueError("Env needs to be one of {}"
                             .format(list(config['accounts'][options.account]['environments'].keys())))
        if not options.stack == config['accounts'][options.account]['environments'][options.env]['stack']:
            raise ValueError("According to the config file stack should be set to {} for {}"
                             .format(config['accounts'][options.account]['environments'][options.env]['stack'],
                                     options.env))

    def run(action, stack_dir, lock_table, state_bucket, run_vars, env, stack):

        print("\n".join(["(",
                         "cd {stack_dir}",
                         "rm -rfv .terraform terraform.tfstate.d"])
              .format(env=options.env,
                      stack_dir=stack_dir))

        print(("terraform init \\\n"
               "         -backend-config \"key={stack}-{account}.tfstate\" \\\n"
               "         -backend-config \"bucket={state_bucket}\" \\\n"
               "         -backend-config \"dynamodb_table={lock_table}\"\n"
               .format(stack=stack,
                       account=options.account,
                       lock_table=lock_table,
                       state_bucket=state_bucket,
                       )))

        if stack == 'service':
            print("\n".join(["terraform workspace select {env} || terraform workspace new {env}"])
                  .format(env=options.env))

        print(("terraform {action} \\\n"
               "{run_vars}"
               ")\n"
               .format(action=action,
                       run_vars=run_vars
                       )))
        return True

    stack_dir = "{workdir}/repos/{component}/providers/aws/{stack}".format(workdir=options.workdir,
                                                                           component='terraform',
                                                                           stack=options.stack,
                                                                           account=options.account)
    lock_table = ("{project}-terraform-lock"
                  .format(project=config['project']))
    state_bucket = ("{project}-terraform-{stack}"
                    .format(project=config['project'],
                            stack=options.stack))

    if options.stack == 'global':

        run_vars = ("          -var \"domain={domain}\" \\\n"
                    "          -var \"project={project}\" \\\n"
                    "          -var \"account={account}\" \\\n"
                    "          -var \"prod_account_id={prod_account_id}\" \\\n"
                    "          -var \"nonprod_account_id={nonprod_account_id}\"\n"
                    .format(project=config['project'],
                            account=options.account,
                            domain=config['accounts'][options.account]['domain'],
                            prod_account_id=config['accounts']['prod']['account_id'],
                            nonprod_account_id=config['accounts']['nonprod']['account_id']))

        if options.action == 'up' and options.bootstrap is True:
            print("\n".join(["if ! aws s3 ls s3://{state_bucket}/global-{account}.tfstate; then"])
                  .format(state_bucket=state_bucket,
                          account=options.account))
            if options.account == 'nonprod':
                print("\n".join(["aws s3api create-bucket \\",
                                 "        --bucket {state_bucket}-temp \\",
                                 "        --acl private \\",
                                 "        --region {region} \\",
                                 "        --create-bucket-configuration \\",
                                 "        LocationConstraint={region}",
                                 "aws s3api wait bucket-exists --bucket {state_bucket}-temp"])
                      .format(state_bucket=state_bucket,
                              region=config['accounts'][options.account]['region']))
            print("\n".join(["aws dynamodb create-table \\",
                             "         --region {region} \\",
                             "         --table-name {lock_table}-temp \\",
                             "         --attribute-definitions AttributeName=LockID,AttributeType=S \\",
                             "         --key-schema AttributeName=LockID,KeyType=HASH \\",
                             "         --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1",
                             "aws dynamodb wait table-exists --table-name {lock_table}-temp"])
                  .format(lock_table=lock_table,
                          region=config['accounts'][options.account]['region']))

            if options.account == 'nonprod':
                run(action, stack_dir, lock_table + "-temp", state_bucket + "-temp",
                    run_vars, options.env, options.stack)
                print("\n".join(["aws s3 mv \\",
                                 "        s3://{state_bucket}-temp/global-{account}.tfstate \\",
                                 "        s3://{state_bucket}/global-{account}.tfstate",
                                 "aws s3api delete-bucket \\",
                                 "        --bucket {state_bucket}-temp"])
                      .format(state_bucket=state_bucket,
                              account=options.account))
            else:
                run(action, stack_dir, lock_table + "-temp", state_bucket, run_vars, options.env, options.stack)

            print("\n".join(["aws dynamodb delete-table \\",
                             "        --table-name {lock_table}-temp",
                             "fi"])
                  .format(lock_table=lock_table))

    if options.stack == 'service':

        get_k8s_cluster_elb(options.env)

        run_vars = ("          -var \"domain={domain}\" \\\n"
                    "          -var \"project={project}\" \\\n"
                    "          -var \"kubernetes_api_elb=$K8S_API_ELB\" \\\n"
                    "          -var \"account={account}\"\n"
                    .format(project=config['project'],
                            account=options.account,
                            domain=config['accounts'][options.account]['domain']))

    run(action, stack_dir, lock_table, state_bucket, run_vars, options.env, options.stack)

    return True


def create_kops_state_bucket(config, options):
    print(("aws s3api create-bucket --bucket {project}-{account}-kops \\\n"
           "                        --region {region} \\\n"
           "                        --create-bucket-configuration=LocationConstraint={region}\n"
           "aws s3api put-bucket-versioning --bucket {project}-{account}-kops \\\n"
           "                                --versioning-configuration Status=Enabled\n"
           .format(project=config['project'],
                   account=options.account,
                   region=config['accounts'][options.account]['region'])))
    return True


def get_k8s_cluster_elb(environment):

    print("\n".join(['export  K8S_API_ELB=$(\\',
                     'aws elb describe-load-balancers \\',
                     '        --query \\',
                     '\'LoadBalancerDescriptions[?starts_with(LoadBalancerName, `api-{environment}-`) == `true`].[DNSName]\' --output text)',  # noqa: E501
                     'if [[ -z $K8S_API_ELB ]] ; then echo \'ERROR: No Load-Balancer found. Did Kops complete correctly?\' 2>&1',  # noqa: E501
                     'exit 1 ; fi'
                     ])
          .format(environment=environment))
    return True


def run_kops_update_cluster(cluster):

    print("\n".join(["kops update cluster {cluster} --yes"])
          .format(cluster=cluster))
    return True


def run_kops(config, options):

    if options.env not in list(config['accounts'][options.account]['environments'].keys()):
        raise ValueError("Env needs to be one of {}"
                         .format(list(config['accounts'][options.account]['environments'].keys())))

    if options.bootstrap:
        create_kops_state_bucket(config, options)

    project = config['project']
    action = options.action
    environment = options.env
    account = options.account
    domain = config['accounts'][options.account]['domain']
    cidr = config['estate_cidr']
    region = config['accounts'][options.account]['region']
    cluster = "{environment}.{account}.{project}.k8s.local".format(environment=environment,
                                                                   account=account,
                                                                   project=project)
    state_store = "s3://{project}-{account}-kops".format(project=config['project'],
                                                         account=options.account)
    cluster_config_file = "{workdir}/kops-{cluster}.yaml".format(workdir=options.workdir,
                                                                 cluster=cluster)
    cluster_rsa_key = "{workdir}/kops-{cluster}-id_rsa".format(workdir=options.workdir,
                                                               cluster=cluster)
    cluster_api_elb_name = "api-{environment}-{account}-{project}-k8s".format(environment=environment,
                                                                              account=account,
                                                                              project=project)
    offset = config['accounts'][options.account]['environments'][options.env]['network_offset']

    print(("export KOPS_STATE_STORE={state_store}\n".format(state_store=state_store)))

    if options.action in ['generate']:

        print(("kops create cluster --cloud aws \\\n"
               "                    --encrypt-etcd-storage \\\n"
               "                    --network-cidr {cidr} \\\n"
               "                    --authorization RBAC \\\n"
               "                    --topology private \\\n"
               "                    --networking weave \\\n"
               "                    --node-count 3 \\\n"
               "                    --zones \"{region}a,{region}b,{region}c\"\\\n"
               "                    --node-size m4.2xlarge \\\n"
               "                    --master-zones \"{region}a,{region}b,{region}c\"\\\n"
               "                    --master-size m4.large \\\n"
               "                    --kubernetes-version 1.7.10 \"{cluster}\"\\\n"
               "                    --dry-run \\\n"
               "                    --output yaml\n"
               .format(action=action,
                       cidr=cidr,
                       cluster=cluster,
                       region=region)))

    if options.action in ['delete', 'destroy']:
        print(("kops delete cluster {cluster} --yes\n"
               "rm -v {cluster_rsa_key}\n"
               "rm -v {cluster_rsa_key}.pub\n"
               "rm -v {cluster_config_file}\n"
               .format(cluster=cluster,
                       cluster_rsa_key=cluster_rsa_key,
                       cluster_config_file=cluster_config_file)))

    if options.action in ['up', 'apply', 'create']:

        subnets_19, subnets_22 = generate_subnets(cidr, offset)
        cluster_config_yaml = parsetemplate(readtemplate('kops_cluster.yaml'),
                                            network_cidr=cidr,
                                            cluster=cluster,
                                            external_domain="{}.{}".format(environment, domain),
                                            state_store=state_store,
                                            region=region,
                                            subnets_19=subnets_19,
                                            subnets_22=subnets_22)
        print(("cat > {cluster_config_file} << EOF \n"
               "{cluster_config_yaml}\n"
               "EOF\n\n"
               "kops create -f {cluster_config_file}\n\n"
               "ssh-keygen -t rsa -b 4096 -P '' -C MicroDC -f {cluster_rsa_key} "
               "|| echo '\\nERROR: ssh key already exists. It must be removed.' 2>&1 ; exit 1\n\n"
               "kops create secret --name {cluster} sshpublickey admin -i {cluster_rsa_key}.pub\n\n"
               .format(cluster=cluster,
                       cluster_config_file=cluster_config_file,
                       cluster_config_yaml=cluster_config_yaml,
                       cluster_rsa_key=cluster_rsa_key,
                       cluster_api_elb_name=cluster_api_elb_name)))

        run_kops_update_cluster(cluster)

    return True
