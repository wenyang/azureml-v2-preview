# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from .base import PatchedNested, PatchedSchemaMeta, PatchedBaseSchema
from .command_job import CommandJobSchema, InternalCommandJob
from .online_endpoint_deployment_schema import OnlineEndpointDeploymentSchema, InternalOnlineEndpointDeployment
from .online_endpoint_schema import OnlineEndpointSchema, InternalOnlineEndpoint
from .model import InternalModel, ModelSchema

__all__ = [
    "PatchedBaseSchema",
    "CommandJobSchema",
    "OnlineEndpointSchema",
    "OnlineEndpointDeploymentSchema",
    "InternalCommandJob",
    "InternalOnlineEndpoint",
    "InternalOnlineEndpointDeployment",
    "PatchedNested",
    "PatchedSchemaMeta",
    "InternalModel",
    "ModelSchema"
]
