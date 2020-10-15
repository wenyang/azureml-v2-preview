# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields)
from .base import PatchedSchemaMeta


class ResourceSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(attribute='name')
    id = fields.Str(attribute='id')
    description = fields.Str(attribute='description')
    tags = fields.Dict(keys=fields.Str, attribute='tags')
