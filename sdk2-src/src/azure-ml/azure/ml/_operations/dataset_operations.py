# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import yaml

from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import DataVersionResource, AssetPath, \
    DataVersionResourceArmPaginatedResult

from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._schema.dataset import InternalDataset, DatasetSchema

from typing import Iterable, Union, Dict
from marshmallow import ValidationError, RAISE


class DatasetOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 **kwargs: Dict):
        super(DatasetOperations, self).__init__(workspace_scope)
        self._operation = service_client.data_version
        self._init_kwargs = kwargs

    def list(self, name: str = None) -> Iterable[DataVersionResourceArmPaginatedResult]:
        name, version = self._parse_name_version(name)

        if version:
            return self.get("{}:{}".format(name, version))
        else:
            return self._operation.list(name,
                                        self._subscription_id,
                                        self._resource_group_name,
                                        self._workspace_name,
                                        API_VERSION_2020_09_01_PREVIEW,
                                        **self._init_kwargs)

    def get(self, name: str = None) -> DataVersionResource:
        name, version = self._parse_name_version(name)
        if version is None:
            # TODO: get the latest version instead of the version 1
            version = "1"

        return self._operation.get(name,
                                   version,
                                   self._subscription_id,
                                   self._resource_group_name,
                                   self._workspace_name,
                                   API_VERSION_2020_09_01_PREVIEW,
                                   **self._init_kwargs)

    def create(self,
               name: str = None,
               description: str = None,
               linked_service_id: str = None,
               path: str = None,
               is_directory: bool = False,
               file: Union[str, os.PathLike, None] = None) -> DataVersionResource:

        loaded_dataset = self._load_yaml(file)

        name, version = self._parse_name_version(name)
        loaded_dataset.name = name or loaded_dataset.name
        loaded_dataset.version = version or loaded_dataset.version

        loaded_dataset.description = description or loaded_dataset.description
        loaded_dataset.linked_service_id = linked_service_id or loaded_dataset.linked_service_id

        # TODO: add support for multiple path, need to decide whether to expose InternalAssetPath to customers
        if path:
            loaded_dataset.asset_paths = [AssetPath(path=path, is_directory=is_directory)]

        data_resource = loaded_dataset.translate_to_rest_object()
        return self._operation.create_or_update(name,
                                                version,
                                                self._subscription_id,
                                                self._resource_group_name,
                                                self._workspace_name,
                                                API_VERSION_2020_09_01_PREVIEW,
                                                data_resource,
                                                **self._init_kwargs)

    def update(self, name: str = None) -> None:
        raise Exception("Not implemented.")

    def delete(self, name: str = None) -> None:
        name, version = self._parse_name_version(name)
        if version:
            return self._operation.delete(name,
                                          version,
                                          self._subscription_id,
                                          self._resource_group_name,
                                          self._workspace_name,
                                          API_VERSION_2020_09_01_PREVIEW,
                                          **self._init_kwargs)
        else:
            raise Exception("Deletion on the whole lineage is not supported yet.")

    def _parse_name_version(self, name: str) -> (str, str):
        token_list = name.split(':')
        if len(token_list) == 1:
            return name, None
        elif len(token_list) == 2:
            return token_list[0], token_list[1]
        else:
            # Find last occurrence of colon
            last_colon_index = name.rindex(':')
            return name[:last_colon_index], name[last_colon_index:]

    def _load_yaml(self, file: Union[str, os.PathLike, None] = None) -> InternalDataset:
        cfg = {}
        try:
            if file is not None:
                with open(file, 'r') as f:
                    cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            internal_dataset: InternalDataset = DatasetSchema().load(cfg, unknown=RAISE)  # type: ignore
            return internal_dataset
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
