import argparse


def parse_args(argv):
    """
    Parse all command line arguments and return a dict
    """
    parser = argparse.ArgumentParser(description='''Generate shell commands from
                                     a yaml config file to setup MicroDC.''')
    parser.add_argument('--config',
                        metavar='CONFIG',
                        nargs=1,
                        help='The location of th YAML config file')
    parser.add_argument('--account',
                        metavar='ACCOUNT',
                        nargs=1,
                        default='default',
                        help='Set the AWS account to use')

    return parser.parse_args(argv)
