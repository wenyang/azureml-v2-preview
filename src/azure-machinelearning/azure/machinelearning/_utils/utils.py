# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

DEVELOPER_URL_MFE_ENV_VAR = "AZUREML_DEV_URL_MFE"


def _get_developer_override(base_url):
    dev_override_url = os.environ.get(DEVELOPER_URL_MFE_ENV_VAR, base_url)

    enforce_https = dev_override_url.lower().startswith("https")

    return dev_override_url, enforce_https


# https://stackoverflow.com/questions/19053707
def snake_to_camel(text):
    """convert snake name to camel"""
    return re.sub('_([a-zA-Z0-9])', lambda m: m.group(1).upper(), text)


def camel_case_transformer(key, attr_desc, value):
    """transfer string to camel case"""
    return (snake_to_camel(key), value)


def create_session_with_retry(retry=3):
    """
    Create requests.session with retry

    :type retry: int
    rtype: Response
    """
    retry_policy = get_retry_policy(num_retry=retry)

    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retry_policy))
    session.mount('http://', HTTPAdapter(max_retries=retry_policy))
    return session


def get_retry_policy(num_retry=3):
    """
    :return: Returns the msrest or requests REST client retry policy.
    :rtype: urllib3.Retry
    """
    status_forcelist = [413, 429, 500, 502, 503, 504]
    backoff_factor = 0.4
    retry_policy = Retry(
        total=num_retry,
        read=num_retry,
        connect=num_retry,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        # By default this is True. We set it to false to get the full error trace, including url and
        # status code of the last retry. Otherwise, the error message is 'too many 500 error responses',
        # which is not useful.
        raise_on_status=False
    )
    return retry_policy


session = create_session_with_retry()


def get_all_logs(details: object, destination: str):
        """Download all logs for the run to a directory.

        :param destination: The destination path to store logs. If unspecified, a directory named as the run ID
            is created in the user home directory.
        :type destination: str
        :return: A list of names of logs downloaded.
        :rtype: builtin.list
        """

        destination = os.path.join(destination, "assets", "id")
        os.makedirs(destination, exist_ok=True)
        details = get_details_with_logs(details)
        log_files = details["logFiles"]
        downloaded_logs = []
        for log_name in log_files:
            target_path = os.path.join(destination, log_name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w') as file:
                file.write(log_files[log_name])
            downloaded_logs.append(target_path)

        return downloaded_logs


def get_details_with_logs(details: object):
    """Return run status including log file content.

    :return: Returns the status for the run with log file contents.
    :rtype: dict
    """
    details = details.as_dict(key_transformer=camel_case_transformer)
    log_files = details["logFiles"]
    for log_name in log_files:
        content = download_file_stream(log_files[log_name], session)
        log_files[log_name] = content
    return details


def download_file_stream(source_uri: str, session: requests.Session = session):
    """Downloads the url content as a byte stream from the url.

    :return: Returns byte streanm.
    :rtype: bytes
    """
    blob_url = source_uri
    raw = session.get(blob_url)
    return raw.text
