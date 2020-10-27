# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: ignore

from .compute_operations import ComputeOperations
from .datastore_operations import DatastoreOperations
from .job_operations import JobOperations
from .workspace_operations import WorkspaceOperations
from .model_operations import ModelOperations
from .endpoint_operations import EndpointOperations
from .dataset_operations import DatasetOperations
from .code_operations import CodeOperations
from .run_operations import RunOperations
from .environment_operations import EnvironmentOperations

__all__ = [
    "ComputeOperations", "DatastoreOperations", "JobOperations", "ModelOperations", "WorkspaceOperations",
    "DatasetOperations", "EndpointOperations", "CodeOperations", "RunOperations", "EnvironmentOperations"
]
