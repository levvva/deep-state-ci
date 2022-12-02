#!/usr/bin/env python
import argparse
import logging
import sys

from credentials_management import profiles_manager

env_choices = ["leva", "ekscreator"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('text', metavar='TEXT', type=str, nargs='+')

    return parser.parse_args()


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def main() -> int:
    """Echo the input arguments to standard output"""
    configure_logging()
    args = parse_args()

    profiles_manager.authenticate_to_aws("leva", True)
    sys.stdout.write(args.text)
    return 0


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
