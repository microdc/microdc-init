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
           "export AWS_DEFAULT_PROFILE={project}-{account}\n"
           .format(project=config['project'],
                   environment=options.env,
                   account=options.account,
                   cidr=config['estate_cidr'],
                   region=config['accounts'][options.account]['region'])))
    return True


def run_terraform(config, options):
    print(("export TF_PLUGIN_CACHE_DIR=\"/tmp/terraform.d/plugin-cache\""))
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


def kops_runner(config, options):
    if options.bootstrap:
        create_kops_state_bucket(config, options)

    project = config['project']
    action = options.action
    environment_dot = "{}.".format(options.env) if options.env != 'prod' else ''
    environment_dash = "{}-".format(options.env) if options.env != 'prod' else ''
    account = options.account
    domain = config['accounts'][options.account]['domain']
    cidr = config['estate_cidr']
    region = config['accounts'][options.account]['region']
    cluster = "{environment}{account}.{project}.k8s.local".format(environment=environment_dot,
                                                                  account=account,
                                                                  project=project)
    state_store = "s3://{project}-{account}-kops".format(project=config['project'],
                                                         account=options.account)
    cluster_config_file = "{workdir}/kops-{cluster}.yaml".format(workdir=options.workdir,
                                                                 cluster=cluster)
    cluster_rsa_key = "{workdir}/kops-{cluster}-id_rsa".format(workdir=options.workdir,
                                                               cluster=cluster)
    cluster_api_elb_name = "api-{environment}{account}-{project}-k8s".format(environment=environment_dash,
                                                                             account=account,
                                                                             project=project)

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

        subnets_19, subnets_22 = generate_subnets(cidr)
        cluster_config_yaml = parsetemplate(readtemplate('kops_cluster.yaml'),
                                            network_cidr=cidr,
                                            cluster=cluster,
                                            external_domain=domain,
                                            state_store=state_store,
                                            region=region,
                                            subnets_19=subnets_19,
                                            subnets_22=subnets_22)
        print(("cat > {cluster_config_file} << EOF \n"
               "{cluster_config_yaml}\n"
               "EOF\n\n"
               "kops create -f {cluster_config_file}\n\n"
               "ssh-keygen -t rsa -b 4096 -P '' -C MicroDC -f {cluster_rsa_key}\n\n"
               "kops create secret --name {cluster} sshpublickey admin -i {cluster_rsa_key}.pub\n\n"
               "kops update cluster {cluster} --yes\n\n"
               "aws elb describe-load-balancers \\\n"
               "        --query 'LoadBalancerDescriptions[?starts_with(LoadBalancerName, \n"
               "                 `{cluster_api_elb_name}`) == `true`].[DNSName]' \\\n"
               "        --output text\n\n"
               "aws ec2 describe-subnets --query \"Subnets[?Tags[?Key=='Name'&&contains(Value,\n"
               "                                                                        'utility')]].SubnetId\"\\\n"
               "                         --output text | \\\n"
               "xargs aws ec2 create-tags --tags \"Key=kubernetes.io/role/internal-elb,Value=true\" --resources\n"
               .format(cluster=cluster,
                       cluster_config_file=cluster_config_file,
                       cluster_config_yaml=cluster_config_yaml,
                       cluster_rsa_key=cluster_rsa_key,
                       cluster_api_elb_name=cluster_api_elb_name)))

    return True
