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


def download_text_from_url(source_uri: str, session: requests.Session, timeout: tuple = None):
    """
    Downloads the content from an URL
    Returns the Response text
    :return:
    :rtype: str
    """

    if session is None:
        session = create_session_with_retry()
    response = session.get(source_uri, timeout=timeout)

    # Match old behavior from execution service's status API.
    if response.status_code == 404:
        return ""

    #_raise_request_error(response, "Retrieving content from " + uri)
    return response.text
