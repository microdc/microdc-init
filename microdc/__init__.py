import sys
from microdc.parse_arguments import parse_args
from microdc.yaml_loader import readyaml


def main():
    args = parse_args(sys.argv[1:])
    microdc_config = readyaml(args.config[0])
    print(microdc_config)

    return True


if __name__ == "__main__":
    main()
