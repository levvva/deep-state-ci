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


def authenticate_to_aws(profile: str, set_default_profile: bool = False) -> None:
    base_profile = _base_profile_name(profile)
    if not aws_credentials_file.profile_exists(base_profile):
        _init_profile(base_profile, profile)

    existing_credentials = aws_credentials_file.get_profile_credentials(profile.lower())
    if existing_credentials and _is_credentials_valid(existing_credentials, profile):
        if set_default_profile:
            backup_default_profile()
            aws_credentials_file.set_profile(DEFAULT_PROFILE, existing_credentials)
        return

    credentials = aws_credentials_file.get_profile_credentials(base_profile)
    mfa_serial_number = _get_mfa_serial_number(credentials)
    mfa_code = input(f'Profile \"{profile}\": Enter MFA code:  ')
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

    aws_credentials_file.set_profile(profile.lower(), temporary_credentials)
    aws_environment_variables_setter.set_aws_environment_variables(temporary_credentials)


def backup_default_profile():
    if aws_credentials_file.profile_exists(DEFAULT_PROFILE) \
            and not aws_credentials_file.profile_exists(DEFAULT_PROFILE_BACKUP):
        aws_credentials_file.rename_profile(DEFAULT_PROFILE, DEFAULT_PROFILE_BACKUP)


def delete_base_profile(profile: str):
    aws_credentials_file.delete_profile(_base_profile_name(profile))


def restore_default_profile() -> None:
    aws_credentials_file.rename_profile(DEFAULT_PROFILE_BACKUP, DEFAULT_PROFILE)


def _base_profile_name(profile: str) -> str:
    return f"{profile.lower()}-base"


def _init_profile(base_profile, profile):
    while True:
        credentials = {AWS_ACCESS_KEY_ID: input(f"Profile \"{profile}\": AWS_ACCESS_KEY_ID:  ").strip(),
                       AWS_SECRET_ACCESS_KEY: input(f"Profile \"{profile}\": AWS_SECRET_ACCESS_KEY:  ").strip(),
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


def _is_credentials_valid(credentials, profile):
    aws_environment_variables_setter.set_aws_environment_variables(credentials)
    ec2_client = boto3.client("ec2")
    try:
        zones = ec2_client.describe_availability_zones()
        if zones.get("AvailabilityZones", None):
            return True
        return False
    except ClientError:
        logging.info(f"Profile \"{profile}\": Existing MFA session is invalid")
        return False


# explicitly using credentials, so environment variables do not interfere with how the client
# is obtained
def _get_sts_boto_client(credentials: dict):
    client = boto3.client(
        'sts',
        aws_access_key_id=credentials[AWS_ACCESS_KEY_ID],
        aws_secret_access_key=credentials[AWS_SECRET_ACCESS_KEY])
    return client
