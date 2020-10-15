# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from .command_job import CommandJobSchema, InternalCommandJob
from .online_endpoint_schema import OnlineEndpointSchema

__all__ = [
    "CommandJobSchema",
    "OnlineEndpointSchema",
    "InternalCommandJob"
]
