# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import post_load
from .asset import InternalAssetPath, AssetSchema
from typing import Iterable
from azure.ml._restclient.machinelearningservices.models import DataVersionResource, DataVersion, AssetPath


class InternalDataset():
    def __init__(
            self,
            *,
            name: str = None,
            version: str = None,
            description: str = None,
            linked_service_id: str = None,
            asset_paths: Iterable[InternalAssetPath] = None, **kwargs):

        self.name = name
        self.version = version
        self.description = description
        self.linked_service_id = linked_service_id
        self.asset_paths = asset_paths

    def translate_to_rest_object(self) -> DataVersionResource:
        path_list = []
        if self.asset_paths:
            for asset_path in self.asset_paths:
                path_list.append(AssetPath(path=asset_path.path, is_directory=asset_path.is_directory))

        dataset_version = DataVersion(dataset_type="simple", description=self.description, asset_paths=path_list)

        return DataVersionResource(properties=dataset_version)


class DatasetSchema(AssetSchema):

    @post_load
    def make(self, data, **kwargs):
        return InternalDataset(**data)
