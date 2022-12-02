#!/usr/bin/env python
import argparse
import json
import logging
import re
import sys

import boto3

from credentials_management import profiles_manager

env_choices = ["leva", "ekscreator"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'))

    return parser.parse_args()


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def main() -> int:
    """Echo the input arguments to standard output"""
    configure_logging()
    args = parse_args()

    profiles_manager.authenticate_to_aws("leva", True)
    s = set()
    for line in args.file.readlines():
        if match := re.search(".*(Encoded authorization failure message: (.*))", line):
            client = boto3.client('sts')
            response = client.decode_authorization_message(
                EncodedMessage=match.group(2)
            )
            decoded_message_json = json.loads(response['DecodedMessage'])
            s.add(decoded_message_json['context']['action'])
    print(list(s))
    return 0


if __name__ == '__main__':
    sys.exit(main())  # next section explains the use of sys.exit
