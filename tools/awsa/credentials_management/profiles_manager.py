import logging
import re

import boto3
from botocore.exceptions import ClientError

from credentials_management import aws_credentials_file, aws_environment_variables_setter
from credentials_management.aws_credentials_file import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, \
    REGION
from credentials_management.consts import DEFAULT_REGION

DEFAULT_PROFILE = "default"
DEFAULT_PROFILE_BACKUP = DEFAULT_PROFILE + "-backup"
MFA_EXPIRATION_SECONDS = 60 * 60 * 24

def authenticate_to_aws(environment: str, set_default_profile: bool = False) -> None:
    base_profile = _base_profile_name(environment)
    if not aws_credentials_file.profile_exists(base_profile):
        _init_profile(base_profile, environment)

    existing_credentials = aws_credentials_file.get_profile_credentials(environment.lower())
    if existing_credentials and _is_credentials_valid(existing_credentials, environment):
        if set_default_profile:
            backup_default_profile()
            aws_credentials_file.set_profile(DEFAULT_PROFILE, existing_credentials)
        return

    credentials = aws_credentials_file.get_profile_credentials(base_profile)
    mfa_serial_number = _get_mfa_serial_number(credentials)
    mfa_code = input(f'Please enter your MFA code for the {environment} AWS account:  ')
    sts_boto_client = _get_sts_boto_client(credentials)

    get_session_token_response = sts_boto_client.get_session_token(
        DurationSeconds=MFA_EXPIRATION_SECONDS,
        SerialNumber=mfa_serial_number,
        TokenCode=str(mfa_code))['Credentials']

    # doing this to preserve any keys in base profile, like 'region'
    temporary_credentials = credentials.copy()
    temporary_credentials.update({
        AWS_ACCESS_KEY_ID: get_session_token_response["AccessKeyId"],
        AWS_SECRET_ACCESS_KEY: get_session_token_response["SecretAccessKey"],
        AWS_SESSION_TOKEN: get_session_token_response["SessionToken"]
    })

    if set_default_profile:
        backup_default_profile()
        aws_credentials_file.set_profile(DEFAULT_PROFILE, temporary_credentials)

    aws_credentials_file.set_profile(environment.lower(), temporary_credentials)
    aws_environment_variables_setter.set_aws_environment_variables(temporary_credentials)


def backup_default_profile():
    if aws_credentials_file.profile_exists(DEFAULT_PROFILE) \
            and not aws_credentials_file.profile_exists(DEFAULT_PROFILE_BACKUP):
        aws_credentials_file.rename_profile(DEFAULT_PROFILE, DEFAULT_PROFILE_BACKUP)


def delete_base_profile(environment: str):
    aws_credentials_file.delete_profile(_base_profile_name(environment))


def restore_default_profile() -> None:
    aws_credentials_file.rename_profile(DEFAULT_PROFILE_BACKUP, DEFAULT_PROFILE)


def _base_profile_name(environment: str) -> str:
    return f"{environment.lower()}-base"


def _init_profile(base_profile, environment):
    while True:
        credentials = {AWS_ACCESS_KEY_ID: input(f"{environment} AWS Access Key ID:  ").strip(),
                       AWS_SECRET_ACCESS_KEY: input(f"{environment} AWS Secret Access Key:  ").strip(),
                       REGION: DEFAULT_REGION}
        try:
            _get_mfa_serial_number(credentials)
            aws_credentials_file.set_profile(base_profile, credentials)
            return
        except ClientError:
            logging.error("Invalid credentials, please try again")


def _get_mfa_serial_number(credentials):
    client = _get_sts_boto_client(credentials)
    caller_arn = client.get_caller_identity()['Arn']
    return re.sub(
        'arn:aws:iam::(\\d+):user/(.+)',
        r'arn:aws:iam::\1:mfa/\2',
        caller_arn
    )


def _is_credentials_valid(credentials, environment):
    aws_environment_variables_setter.set_aws_environment_variables(credentials)
    ec2client = boto3.client("ec2")
    try:
        ec2client.describe_instances()
        return True
    except ClientError:
        logging.info(f"Previous {environment} MFA session is invalid")
        return False


# explicitly using credentials, so environment variables do not interfere with how the client
# is obtained
def _get_sts_boto_client(credentials: dict):
    client = boto3.client(
        'sts',
        aws_access_key_id=credentials[AWS_ACCESS_KEY_ID],
        aws_secret_access_key=credentials[AWS_SECRET_ACCESS_KEY])
    return client
