#!/usr/bin/env python
import sys
from microdc.parse_arguments import parse_args

def main(argv):
    args = parse_args(argv)
    print(args)

if __name__ == "__main__":
    main(sys.argv[1:])
