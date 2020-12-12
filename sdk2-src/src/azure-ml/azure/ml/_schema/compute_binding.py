# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from azure.ml.constants import AssetType
from .schema import PatchedSchemaMeta
from .fields import ArmStr
from azure.ml._restclient.machinelearningservices.models import ComputeBinding


class ComputeBindingSchema(metaclass=PatchedSchemaMeta):
    compute_id = ArmStr(data_key="target", asset_type=AssetType.COMPUTE, name="target")
    node_count = fields.Integer()

    @post_load
    def make(self, data, **kwargs) -> ComputeBinding:
        return ComputeBinding(**data)
