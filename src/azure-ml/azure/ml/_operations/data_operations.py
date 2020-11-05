# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import yaml

from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import DataVersionResource, DataVersionResourceArmPaginatedResult
from azure.ml._operations import DatastoreOperations
from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml._utils._arm_id_utils import get_datastore_arm_id

from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY
from azure.ml._schema.asset import InternalAsset, AssetSchema

from typing import Iterable, Tuple, Union, Dict
from marshmallow import ValidationError, RAISE
from pathlib import Path


class DataOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope,
                 service_client: AzureMachineLearningWorkspaces,
                 datastore_operations: DatastoreOperations,
                 **kwargs: Dict):

        super(DataOperations, self).__init__(workspace_scope)
        self._operation = service_client.data_version
        self._datastore_operations = datastore_operations
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
               file_path: Union[str, os.PathLike] = None,
               directory_path: Union[str, os.PathLike] = None,
               yaml_path: Union[str, os.PathLike, None] = None) -> DataVersionResource:

        loaded_data = self._load_yaml(yaml_path)

        name, version = self._parse_name_version(name)
        loaded_data.name = name or loaded_data.name
        loaded_data.version = version or loaded_data.version

        loaded_data.description = description or loaded_data.description
        loaded_data.linked_service_id = linked_service_id or loaded_data.linked_service_id

        if file_path and directory_path:
            raise Exception("The asset needs to point to either a file or a folder.")
        elif file_path or directory_path:
            # overwriting from directly passed in arguments
            loaded_data.file = file_path
            loaded_data.directory = directory_path
        else:
            # load file/directory from yaml
            pass

        data_resource = loaded_data.to_data_version()
        return self._operation.create_or_update(loaded_data.name,
                                                loaded_data.version,
                                                self._subscription_id,
                                                self._resource_group_name,
                                                self._workspace_name,
                                                API_VERSION_2020_09_01_PREVIEW,
                                                data_resource,
                                                **self._init_kwargs)

    def upload(self,
               name: str,
               description: str,
               local_path: Union[str, os.PathLike],
               linked_service_name: str = None) -> DataVersionResource:

        path = Path(local_path)
        is_directory = path.is_dir()

        datastore_name = linked_service_name or self._datastore_operations.get_default().name
        asset_path = upload_artifact(path, self._datastore_operations, datastore_name, include_container_in_asset_path=True)
        datastore_resource_id = get_datastore_arm_id(datastore_name, self._workspace_scope)
        if is_directory:
            return self.create(name=name, description=description, linked_service_id=datastore_resource_id, directory_path=asset_path)
        else:
            return self.create(name=name, description=description, linked_service_id=datastore_resource_id, file_path=asset_path)

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

    def _parse_name_version(self, name: str) -> Tuple[str, str]:
        if not name:
            return None, None

        token_list = name.split(':')
        if len(token_list) == 1:
            return name, None
        else:
            *name, version = token_list
            return ":".join(name), version

    def _load_yaml(self, file: Union[str, os.PathLike, None] = None) -> InternalAsset:
        cfg = {}
        base_path = Path().resolve()
        try:
            if file is not None:
                base_path = Path(file).parent
                with open(file, 'r') as f:
                    cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            internal_asset: InternalAsset = AssetSchema(context={BASE_PATH_CONTEXT_KEY: base_path}).load(cfg, unknown=RAISE)  # type: ignore
            return internal_asset
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
