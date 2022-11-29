import re
import os
import itertools

AWS_ACCESS_KEY_ID = 'aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'aws_secret_access_key'
AWS_SESSION_TOKEN = 'aws_session_token'
REGION = 'region'

# dict of dicts, eg: { 'eks': { 'aws_access_key_id':'FGTACAECA12DF', ... }}
_aws_profiles = {}


def profile_exists(profile_name: str) -> bool:
    return profile_name in _aws_profiles


def get_profile_credentials(profile_name: str) -> dict:
    return _aws_profiles[profile_name] if profile_exists(profile_name) else None


def set_profile(profile_name: str, credentials: dict) -> None:
    _aws_profiles[profile_name] = credentials
    _save()


def rename_profile(source_profile_name: str, target_profile_name: str) -> None:
    _aws_profiles[target_profile_name]=_aws_profiles.pop(source_profile_name)
    _save()


def delete_profile(profile_name: str) -> None:
    _aws_profiles.pop(profile_name, None)
    _save()


def _read_profiles_from_credentials_file(credentials_file: str):
    with open(credentials_file,'r') as file:
        for profile_key, profile_creds in itertools.groupby(file, lambda line: re.match('\[(.*)\]', line)):
            if profile_key:
                profile_name = profile_key.group(1)
                continue
            profile_credentials = {}
            for cred_key_value_line in [line.strip() for line in list(profile_creds) if line.strip()]:
                cred_key, cred_value = cred_key_value_line.split("=", 1)
                profile_credentials[cred_key] = cred_value
            yield profile_name, profile_credentials


def _get_aws_credentials_file_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".aws", "credentials")


def _load() -> None:
    if not os.path.isfile(_get_aws_credentials_file_path()):
        return
    for profile_name, profile_credentials in _read_profiles_from_credentials_file(_get_aws_credentials_file_path()):
        _aws_profiles[profile_name] = profile_credentials


def _save() -> None:
    with open(_get_aws_credentials_file_path(), "w") as aws_credentials_file:
        for profile_name, credentials in _aws_profiles.items():
            aws_credentials_file.write(f"[{profile_name}]\n")
            aws_credentials_file.writelines([f"{k}={v}\n" for (k,v) in credentials.items()])
            aws_credentials_file.write("\n")


_load()
