# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from .base import PatchedSchemaMeta
from .._restclient.machinelearningservices.models import ComputeBinding


class ComputeBindingSchema(metaclass=PatchedSchemaMeta):
    compute_id = fields.Str(data_key="target")
    node_count = fields.Integer()

    @post_load
    def make(self, data, **kwargs) -> ComputeBinding:
        return ComputeBinding(**data)
