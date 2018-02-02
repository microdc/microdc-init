import argparse
import os
import sys
from datetime import datetime


def check_date_file(datefile):
    try:
        with open(datefile, 'r') as file:
            date = file.readline().strip()
        file.close()
        datetime.strptime(date, '%d %b %Y %H:%M')
        return True
    except ValueError:
        raise ValueError("Date in {} is wrong".format(datefile))
    except FileNotFoundError:
        return False


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
    parser.add_argument('--stack',
                        metavar='STACK',
                        help='Which stack to apply')
    parser.add_argument('--tool',
                        metavar='TOOL',
                        help='Which tool to use')
    parser.add_argument('--account',
                        metavar='ACCOUNT',
                        default='nonprod',
                        help='Set the AWS account to use')
    parser.add_argument('--bootstrap',
                        action='store_true',
                        help='Run bootsrap steps')
    parser.add_argument('--env',
                        metavar='ENV',
                        default='None',
                        help='Which environment to modify')
    parser.add_argument('--datefile',
                        metavar='DATEFILE',
                        default='.datefile',
                        help='The datefile is used to check fi the setup process has been run.\
                              Defaults to .datefile in the workdir.')
    parser.add_argument('--setup',
                        action='store_true',
                        help='Download MicroDC components')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='Overwrite the various MicroDC component repos when using --setup')
    parser.add_argument('--workdir',
                        metavar='WORKDIR',
                        help='MicroDC working folder eg. /home/user/.microdc')
    parser.add_argument('action',
                        metavar='ACTION',
                        help='Action to perform: up or dowm')

    arguments = parser.parse_args(argv)
    if not check_date_file("{}/{}".format(arguments.workdir, arguments.datefile)):
        if not arguments.setup:
            parser.print_help()
            print("\nERR please run with --setup\n")
            sys.exit(2)

    return arguments
