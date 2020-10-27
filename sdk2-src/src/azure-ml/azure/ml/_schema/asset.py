# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from .resource import ResourceSchema
from .base import PatchedSchemaMeta


class InternalAssetPath:
    def __init__(self, path: str, is_directory: bool):
        self.path = path
        self.is_directory = is_directory


class AssetPathSchema(metaclass=PatchedSchemaMeta):
    path = fields.Str()
    is_directory = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        return InternalAssetPath(**data)


class AssetSchema(ResourceSchema):
    # Open question, in yaml do we have dedicated field for version?
    version = fields.Str()
    linked_service_id = fields.Str(data_key='linkedServiceId')
    asset_paths = fields.List(fields.Nested(AssetPathSchema), data_key="assetPaths")
