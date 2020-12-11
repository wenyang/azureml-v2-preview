# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

MFE_BASE_URL = "https://management.azure.com"
API_VERSION_2020_12_01_PREVIEW = "2020-12-01-preview"
API_VERSION_2020_09_01_PREVIEW = "2020-09-01-preview"
ONLINE_ENDPOINT_TYPE = "online"
BATCH_ENDPOINT_TYPE = "batch"
BASE_PATH_CONTEXT_KEY = "base_path"
PARAMS_OVERRIDE_KEY = "params_override"
WORKSPACE_CONTEXT_KEY = "workspace"
JOB_TYPE = "job_type"
ARM_ID_PREFIX = "azureml:"
YAML_FILE_PREFIX = "file:"
ARM_ID_FULL_PREFIX = "/subscriptions/"
AZUREML_RESOURCE_PROVIDER = "Microsoft.MachineLearningServices"
RESOURCE_ID_FORMAT = "/subscriptions/{}/resourceGroups/{}/providers/" "{}/workspaces/{}"
PYTHON = "python"
AMLTOKEN = "AMLToken"
KEY = "KEY"


class ComputeType(object):
    AKS = "AKS"
    MANAGED = "managed"


class DistributionType(object):
    MPI = "Mpi"
    TENSORFLOW = "TensorFlow"
    PYTORCH = "PyTorch"


class EndpointDeploymentLogContainerType(object):
    STORAGE_INITIALIZER_REST = "StorageInitializer"
    INFERENCE_SERVER_REST = "InferenceServer"
    INFERENCE_SERVER = "inference-server"
    STORAGE_INITIALIZER = "storage-initializer"


class JobType(object):
    COMMAND = "Command"
    SWEEP = "Sweep"


class AssetType(object):
    CODE = "codes"
    COMPUTE = "computes"
    DATA = "data"
    ENVIRONMENT = "environments"
    MODEL = "models"
    DATASTORE = "datastores"


class ScaleSettingsType(object):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class ArmConstants(object):
    CODE_PARAMETER_NAME = "codes"
    CODE_VERSION_PARAMETER_NAME = "codeVersions"
    MODEL_PARAMETER_NAME = "models"
    MODEL_VERSION_PARAMETER_NAME = "modelVersions"
    ENVIRONMENT_PARAMETER_NAME = "environments"
    WORKSPACE_PARAMETER_NAME = "workspaceName"
    LOCATION_PARAMETER_NAME = "location"
    ENDPOINT_PARAMETER_NAME = "onlineEndpoint"
    ENDPOINT_NO_TRAFFIC_PARAMETER_NAME = "onlineEndpointNoTraffic"
    PROPERTIES_WITH_TRAFFIC_PARAMETER_NAME = "propertiesWithTraffic"
    DEPLOYMENTS_PARAMETER_NAME = "deployments"
    PROPERTIES_PARAMETER_NAME = "properties"
    DEPENDSON_PARAMETER_NAME = "dependsOn"
    TRAFFIC_PARAMETER_NAME = "trafficRules"
    CODE_RESOURCE_NAME = "codeDeploymentCopy"
    CODE_VERSION_RESOURCE_NAME = "codeVersionDeploymentCopy"
    MODEL_RESOURCE_NAME = "modelDeploymentCopy"
    MODEL_VERSION_RESOURCE_NAME = "modelVersionDeploymentCopy"
    ENVIRONMENT_VERSION_RESOURCE_NAME = "environmentVersionDeploymentCopy"
    ONLINE_DEPLOYMENT_RESOURCE_NAME = "onlineDeploymentCopy"
    ONLINE_ENDPOINT_RESOURCE_NAME = "onlineEndpointCopy"
    UPDATE_RESOURCE_NAME = "updateEndpointWithTraffic"

    CODE_TYPE = "code"
    CODE_VERSION_TYPE = "code_version"
    MODEL_TYPE = "model"
    MODEL_VERSION_TYPE = "model_version"
    ENVIRONMENT_VERSION_TYPE = "environment_version"
    ONLINE_ENDPOINT_TYPE = "online_endpoint"
    ONLINE_DEPLOYMENT_TYPE = "online_deployment"
    UPDATE_ONLINE_ENDPOINT_TYPE = "update_online_endpoint"
    BASE_TYPE = "base"

    NAME = "name"
    VERSION = "version"
    ASSET_PATH = "assetPath"
    DATASTORE_ID = "datastoreId"
    OBJECT = "Object"
    ARRAY = "Array"
    DEFAULT_VALUE = "defaultValue"

    AZURE_MGMT_RESOURCE_API_VERSION = "2020-06-01"


class OperationTypes(object):
    WORKSPACES = "workspaces"
    COMPUTES = "computes"
    DATASTORES = "datastores"
    MODELS = "models"
    ENDPOINTS = "endpoints"
    DATASETS = "datasets"
    CODES = "codes"
    JOBS = "jobs"
    ENVIRONMENTS = "environments"
