# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore

from .compute_operations import ComputeOperations
from .datastore_operations import DatastoreOperations
from .job_operations import JobOperations
from .workspace_operations import WorkspaceOperations
from .model_operations import ModelOperations
from .online_endpoint_operations import OnlineEndpointOperations
from .online_endpoint_deployment_operations import OnlineEndpointDeploymentOperations
from .dataset_operations import DatasetOperations
from .code_operations import CodeOperations
from .run_operations import RunOperations

__all__ = [
    "ComputeOperations", "DatastoreOperations", "JobOperations", "ModelOperations", "WorkspaceOperations",
    "DatasetOperations", "OnlineEndpointOperations", "CodeOperations", "RunOperations",
    "OnlineEndpointDeploymentOperations"
]
