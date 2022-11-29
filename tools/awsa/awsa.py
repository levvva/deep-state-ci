#!/usr/bin/env python
import argparse
import logging
import sys

from credentials_management import profiles_manager

env_choices = ["leva", "ekscreator"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=env_choices,
                        help="Possible values are: {}".format(",".join(env_choices)))
    parser.add_argument("--clear", action="store_true",
                        help="Remove stored keys eg. if access keys changed")
    return parser.parse_args()


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def main() -> int:
    """Echo the input arguments to standard output"""
    configure_logging()
    args = parse_args()
    if args.clear:
        profiles_manager.delete_base_profile(args.profile)

    profiles_manager.authenticate_to_aws(args.profile, True)
    sys.stdout.write(f"Profile \"{args.profile}\": Successfully authenticated")
    return 0


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
