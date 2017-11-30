import sys
from microdc.parse_arguments import parse_args
from microdc.yaml_loader import readyaml
from microdc.output_commands import (setup_environment,
                                     run_terraform,
                                     create_kops_state_bucket,
                                     run_kops)


def main():
    options = parse_args(sys.argv[1:])
    config = readyaml(options.config)

    setup_environment(config, options)

    if options.tool == 'terraform':
        run_terraform(config, options)

    if options.tool == 'kops':
        create_kops_state_bucket(config, options)
        run_kops(config, options)

    return True


if __name__ == "__main__":
    main()
