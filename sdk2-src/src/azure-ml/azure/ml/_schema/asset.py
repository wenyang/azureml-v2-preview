# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional
from marshmallow import fields, post_load
from .resource import ResourceSchema
from .fields import ArmStr
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, AssetType
from azure.ml._restclient.machinelearningservices.models import DataVersionResource, DataVersion, AssetPath, \
    AssetContainerResource


class InternalAsset:
    def __init__(
            self,
            base_path: Optional[str] = None,
            name: str = None,
            version: int = None,
            description: str = None,
            datastore: str = None,
            file: str = None,
            directory: str = None):

        self.name = name
        self.version = version
        self.description = description
        self.datastore = datastore
        self.file = file
        self.directory = directory
        self._base_path = base_path

    @classmethod
    def _from_data_version(cls, name: str, data_version: DataVersionResource):

        asset_path = data_version.properties.asset_path
        # Parsing ARM id to get the version
        version = int(data_version.id.rsplit('/', 1)[1])
        if asset_path.is_directory:
            return InternalAsset(name=name,
                                 version=version,
                                 description=data_version.properties.description,
                                 datastore="azureml:" + data_version.properties.datastore_id,
                                 directory=asset_path.path)
        else:
            return InternalAsset(name=name,
                                 version=version,
                                 description=data_version.properties.description,
                                 datastore="azureml:" + data_version.properties.datastore_id,
                                 file=asset_path.path)

    @classmethod
    def _from_data_container(cls, data_container: AssetContainerResource):
        return InternalAsset(name=data_container.name, version=1)

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
                                      datastore_id=self.datastore)
        return DataVersionResource(properties=dataset_version)


class AssetSchema(ResourceSchema):
    # Open question, in yaml do we have dedicated field for version?
    version = fields.Int()
    datastore = ArmStr(asset_type=AssetType.DATASTORE)
    file = fields.Str()
    directory = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return InternalAsset(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
