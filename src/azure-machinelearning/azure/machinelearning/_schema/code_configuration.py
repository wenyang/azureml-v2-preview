# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from .base import PatchedSchemaMeta
from .._restclient.machinelearningservices.models import CodeConfiguration


class CodeConfigurationSchema(metaclass=PatchedSchemaMeta):
    code_artifact_id = fields.Str()
    command = fields.List(fields.Str())

    @post_load
    def make(self, data, **kwargs):
        return CodeConfiguration(**data)
