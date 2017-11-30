import argparse


def parse_args(argv):
    """
    Parse all command line arguments and return a dict
    """
    parser = argparse.ArgumentParser(description='''Generate shell commands from
                                     a yaml config file to setup MicroDC.''')
    required = parser.add_argument_group('required arguments')
    required.add_argument('--config',
                          metavar='CONFIG',
                          required=2,
                          help='The location of the YAML config file')
    required.add_argument('--env',
                          metavar='ENV',
                          required=2,
                          help='Which environment to modify')
    required.add_argument('--stack',
                          metavar='STACK',
                          required=2,
                          help='Which stack to apply')
    required.add_argument('--tool',
                          metavar='TOOL',
                          default='all',
                          help='Which tool to use')
    parser.add_argument('--account',
                        metavar='ACCOUNT',
                        default='default',
                        help='Set the AWS account to use')
    parser.add_argument('action',
                        metavar='ACTION',
                        help='Action to perform: up or dowm')

    return parser.parse_args(argv)
