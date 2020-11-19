# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

MFE_BASE_URL = "https://centraluseuap.management.azure.com"
API_VERSION_2020_12_01_PREVIEW = "2020-12-01-preview"
API_VERSION_2020_09_01_PREVIEW = "2020-09-01-preview"
ONLINE_ENDPOINT_TYPE = "online"
BATCH_ENDPOINT_TYPE = "batch"
BASE_PATH_CONTEXT_KEY = "base_path"
PARAMS_OVERRIDE_KEY = "params_override"
WORKSPACE_CONTEXT_KEY = "workspace"
COMMAND = "Command"
SWEEP = "Sweep"
JOB_TYPE = "job_type"
ARM_ID_PREFIX = 'azureml:'
YAML_FILE_PREFIX = 'file:'
ARM_ID_FULL_PREFIX = "/subscriptions/"
AZUREML_RESOURCE_PROVIDER = "Microsoft.MachineLearningServices"
RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/" \
                     "{}/workspaces/{}"
PYTHON = "python"


class AssetType(object):
    CODE = "codes"
    COMPUTE = "computes"
    DATA = "data"
    ENVIRONMENT = "environments"
    MODEL = "models"
