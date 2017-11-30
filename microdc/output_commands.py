def setup_environment(config, options):
    required_config_values = ['project',
                              'estate_cidr',
                              'accounts']
    for value in required_config_values:
        if value not in config:
            raise ValueError("\'{}\' missing from config".format(value))

    required_option_values = ['env',
                              'account']
    for value in required_option_values:
        if value not in options:
            raise ValueError("\'{}\' missing from options".format(value))

    if not options.account in config['accounts']:
        raise ValueError("\'{}\' missing from options".format(options.account))

    print(("export PROJECT={0}\n"
           "export ENVIRONMENT={1}\n"
           "export ACCOUNT={2}\n"
           "export CIDR={3}\n"
           "export AWS_DEFAULT_REGION={4}\n"
           "export AWS_DEFAULT_PROFILE=\"${{PROJECT}}-${{ACCOUNT}}\"\n"
           "export CLUSTER=\"${{ENVIRONMENT}}.${{ACCOUNT}}.${{PROJECT}}.k8s.local\"\n"
           "export KOPS_STATE_STORE=\"s3://${{AWS_DEFAULT_PROFILE}}-kops\"\n"
    .format(config['project'],
               options.env,
               options.account,
               config['estate_cidr'],
               config['accounts'][options.account]['region'])))
    return True

def run_terraform(config, options):
    print(("export TF_PLUGIN_CACHE_DIR=\"/tmp/terraform.d/plugin-cache\""))
    return True

def create_kops_state_bucket(config, options):
    print(("aws s3api create-bucket --bucket ${KOPS_STATE_STORE} \\\n"
           "                        --region ${AWS_DEFAULT_REGION} \\\n"
           "                        --create-bucket-configuration=LocationConstraint=${AWS_DEFAULT_REGION}\n"
           "aws s3api put-bucket-versioning --bucket ${KOPS_STATE_STORE} \\\n"
           "                                --versioning-configuration Status=Enabled\n"))
    return True

def run_kops(config, options):
    print(("kops create cluster --cloud aws \\\n"
           "                    --encrypt-etcd-storage \\\n"
           "                    --network-cidr ${CIDR} \\\n"
           "                    --authorization RBAC \\\n"
           "                    --topology private \\\n"
           "                    --networking weave \\\n"
           "                    --node-count 3 \\\n"
           "                    --zones \"${AWS_DEFAULT_REGION}a,${AWS_DEFAULT_REGION}b,${AWS_DEFAULT_REGION}c\"\\\n"
           "                    --node-size m4.2xlarge \\\n"
           "                    --master-zones \"${AWS_DEFAULT_REGION}a,${AWS_DEFAULT_REGION}b,${AWS_DEFAULT_REGION}c\"\\\n"
           "                    --master-size m4.large \\\n"
           "                    --kubernetes-version 1.7.10 \"${CLUSTER}\"\n"))
    return True
