import sys
from microdc.parse_arguments import parse_args
from microdc.yaml_loader import readyaml, check_config
from microdc.output_commands import (setup_environment,
                                     setup_microdc_workarea,
                                     run_kubectl,
                                     run_terraform,
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

    actions = ["up", "down"]
    if options.action not in actions:
        raise ValueError("{} is not supported - Action should be one of {}".format(options.action, actions))

    tools = ["kops", "terraform", "kubectl"]
    try:
        globals()["run_{}".format(options.tool)](config, options)
    except KeyError:
        raise ValueError("{} is not supported - tool should be one of {}".format(options.tool, tools))

    return True


if __name__ == "__main__":
    main()
