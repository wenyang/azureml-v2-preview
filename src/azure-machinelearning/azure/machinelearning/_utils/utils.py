# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os

DEVELOPER_URL_MFE_ENV_VAR = "AZUREML_DEV_URL_MFE"


def _get_developer_override(base_url):
    dev_override_url = os.environ.get(DEVELOPER_URL_MFE_ENV_VAR, base_url)

    enforce_https = dev_override_url.lower().startswith("https")

    return dev_override_url, enforce_https
