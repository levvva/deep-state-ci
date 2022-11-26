import os

from credentials_management import aws_credentials_file

_credentials_key_name_to_environment_variables_names_dict = {
    aws_credentials_file.AWS_ACCESS_KEY_ID: "AWS_ACCESS_KEY_ID",
    aws_credentials_file.AWS_SECRET_ACCESS_KEY: "AWS_SECRET_ACCESS_KEY",
    aws_credentials_file.AWS_SESSION_TOKEN: "AWS_SESSION_TOKEN",
    aws_credentials_file.REGION: "AWS_DEFAULT_REGION"
}


def set_aws_environment_variables(credentials: dict):
    for cred_key, cred_value in credentials.items():
        envvar_name = _credentials_key_name_to_environment_variables_names_dict.get(cred_key)
        if envvar_name:
            os.environ[envvar_name] = cred_value
