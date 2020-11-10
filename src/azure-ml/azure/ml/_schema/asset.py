# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional
from marshmallow import fields, post_load
from .resource import ResourceSchema
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ml._restclient.machinelearningservices.models import DataVersionResource, DataVersion, AssetPath


class InternalAsset:
    def __init__(
            self,
            base_path: Optional[str] = None,
            *,
            name: str = None,
            version: str = None,
            description: str = None,
            linked_service_id: str = None,
            file: str = None,
            directory: str = None, **kwargs):

        self.name = name
        self.version = version
        self.description = description
        self.linked_service_id = linked_service_id
        self.file = file
        self.directory = directory
        self._base_path = base_path

    def to_data_version(self) -> DataVersionResource:

        asset_path = None
        if self.file and self.directory:
            raise Exception("The asset needs to point to either a file or a folder.")
        elif self.file:
            asset_path = AssetPath(path=self.file, is_directory=False)
        elif self.directory:
            asset_path = AssetPath(path=self.directory, is_directory=True)
        else:
            # Neither file nor directory specified in yaml, customers could provide it directly in CLI or SDK too.
            pass

        dataset_version = DataVersion(dataset_type="simple",
                                      description=self.description,
                                      asset_path=asset_path,
                                      datastore_id=self.linked_service_id)
        return DataVersionResource(properties=dataset_version)


class AssetSchema(ResourceSchema):
    # Open question, in yaml do we have dedicated field for version?
    version = fields.Int()
    linked_service_id = fields.Str(data_key='linkedServiceId')
    file = fields.Str()
    directory = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalAsset(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
