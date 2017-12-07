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
