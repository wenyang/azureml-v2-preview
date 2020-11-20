# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from .schema import PatchedSchemaMeta
from azure.ml._restclient.machinelearningservices.models import DataBinding


class DataBindingSchema(metaclass=PatchedSchemaMeta):
    source_data_reference = fields.Str()
    local_reference = fields.Str()
    mode = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return DataBinding(**data)
