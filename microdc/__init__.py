import sys
from microdc.parse_arguments import parse_args
from microdc.yaml_loader import readyaml, check_config
from microdc.output_commands import (setup_environment,
                                     setup_microdc_workarea,
                                     run_terraform,
                                     create_kops_state_bucket,
                                     run_kops)


def main():
    options = parse_args(sys.argv[1:])
    config = readyaml(options.config)
    expected_config_values = ['component_repos',
                              'project',
                              'estate_cidr',
                              'accounts']

    if not check_config(expected_config_values, config):
        sys.exit(1)

    if options.setup:
        setup_microdc_workarea(workdir=options.workdir,
                               component_repos=config['component_repos'],
                               datefile="{}/{}".format(options.workdir, options.datefile),
                               overwrite=options.overwrite if 'overwrite' in options else False)

    setup_environment(config, options)

    if options.tool == 'all':
        print("--tool 'all' - Not implemented, please specify a tool - terraform, kops")

    if options.tool == 'terraform':
        run_terraform(config, options)

    if options.tool == 'kops':
        create_kops_state_bucket(config, options)
        run_kops(config, options)

    return True


if __name__ == "__main__":
    main()
