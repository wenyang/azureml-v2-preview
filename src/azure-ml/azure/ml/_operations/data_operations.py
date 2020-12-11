# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import yaml

from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces,
)
from azure.ml._operations import DatastoreOperations
from azure.ml._artifacts._artifact_utilities import upload_artifact
from azure.ml._utils._arm_id_utils import get_datastore_arm_id

from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW, BASE_PATH_CONTEXT_KEY, WORKSPACE_CONTEXT_KEY
from azure.ml._schema.asset import InternalAsset, AssetSchema

from typing import Union, Dict, List
from marshmallow import ValidationError, RAISE
from pathlib import Path


class DataOperations(_WorkspaceDependentOperations):
    def __init__(
        self,
        workspace_scope: WorkspaceScope,
        service_client: AzureMachineLearningWorkspaces,
        datastore_operations: DatastoreOperations,
        **kwargs: Dict,
    ):

        super(DataOperations, self).__init__(workspace_scope)
        self._operation = service_client.data_versions
        self._container_operation = service_client.data_containers
        self._datastore_operations = datastore_operations
        self._init_kwargs = kwargs

    def list(self, name: str = None) -> List[InternalAsset]:
        if name:
            return list(
                map(
                    lambda data_version: InternalAsset._from_data_version(str(name), data_version),
                    self._operation.list(
                        name,
                        self._subscription_id,
                        self._resource_group_name,
                        self._workspace_name,
                        API_VERSION_2020_09_01_PREVIEW,
                        skip_token=None,
                        **self._init_kwargs,
                    ),
                )
            )
        else:
            return list(
                map(
                    lambda data_container: InternalAsset._from_data_container(data_container),
                    self._container_operation.list(
                        self._subscription_id,
                        self._resource_group_name,
                        self._workspace_name,
                        API_VERSION_2020_09_01_PREVIEW,
                        skip_token=None,
                        **self._init_kwargs,
                    ),
                )
            )

    def get(self, name: str, version: int) -> InternalAsset:
        data_version = self._operation.get(
            name,
            str(version),
            self._subscription_id,
            self._resource_group_name,
            self._workspace_name,
            API_VERSION_2020_09_01_PREVIEW,
            **self._init_kwargs,
        )

        return InternalAsset._from_data_version(name, data_version)

    def create_or_update(
        self,
        name: str = None,
        version: int = None,
        description: str = None,
        linked_service_id: str = None,
        file_path: Union[str, os.PathLike] = None,
        directory_path: Union[str, os.PathLike] = None,
        yaml_path: Union[str, os.PathLike, None] = None,
    ) -> InternalAsset:

        loaded_data = self._load_yaml(yaml_path)

        loaded_data.name = name or loaded_data.name
        loaded_data.version = version if version else loaded_data.version

        if loaded_data.name is None or loaded_data.version is None:
            raise Exception(
                'Name and version are required, please provide name and version in "<name>:<version>" format or in yaml file.'
            )

        loaded_data.description = description or loaded_data.description
        loaded_data.datastore = linked_service_id or loaded_data.datastore

        if file_path and directory_path:
            raise Exception("The asset needs to point to either a file or a folder.")
        elif file_path or directory_path:
            # overwriting from directly passed in arguments
            loaded_data.file = str(file_path) if file_path else loaded_data.file
            loaded_data.directory = str(directory_path) if directory_path else loaded_data.directory
        else:
            # load file/directory from yaml
            pass

        data_resource = loaded_data.to_data_version()
        result = self._operation.create_or_update(
            str(loaded_data.name),
            str(loaded_data.version),
            self._subscription_id,
            self._resource_group_name,
            self._workspace_name,
            API_VERSION_2020_09_01_PREVIEW,
            data_resource,
            **self._init_kwargs,
        )
        return InternalAsset._from_data_version(str(loaded_data.name), result)

    def upload(
        self,
        name: str,
        version: int,
        local_path: Union[str, os.PathLike],
        description: str = None,
        linked_service_name: str = None,
    ) -> InternalAsset:

        path = Path(local_path)
        is_directory = path.is_dir()

        datastore_name = linked_service_name or self._datastore_operations.get_default().name
        asset_path = upload_artifact(
            str(path), self._datastore_operations, datastore_name, include_container_in_asset_path=False
        )
        datastore_resource_id = get_datastore_arm_id(str(datastore_name), self._workspace_scope)
        if is_directory:
            return self.create_or_update(
                name=name,
                version=version,
                description=description,
                linked_service_id=datastore_resource_id,
                directory_path=asset_path.path,
            )
        else:
            return self.create_or_update(
                name=name,
                version=version,
                description=description,
                linked_service_id=datastore_resource_id,
                file_path=asset_path.path,
            )

    def delete(self, name: str, version: int) -> None:
        if version:
            return self._operation.delete(
                name,
                str(version),
                self._subscription_id,
                self._resource_group_name,
                self._workspace_name,
                API_VERSION_2020_09_01_PREVIEW,
                **self._init_kwargs,
            )
        else:
            raise Exception("Deletion on the whole lineage is not supported yet.")

    def _load_yaml(self, file: Union[str, os.PathLike, None] = None) -> InternalAsset:
        cfg = {}
        base_path = Path().resolve()
        try:
            if file is not None:
                base_path = Path(file).parent
                with open(file, "r") as f:
                    cfg = yaml.safe_load(f)
        except OSError:  # FileNotFoundError introduced in Python 3
            raise Exception(f"No such file or directory: {file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")

        try:
            internal_asset: InternalAsset = AssetSchema(
                context={BASE_PATH_CONTEXT_KEY: base_path, WORKSPACE_CONTEXT_KEY: self._workspace_scope}
            ).load(
                cfg, unknown=RAISE
            )  # type: ignore
            return internal_asset
        except ValidationError as e:
            raise Exception(f"Error while parsing yaml file: {file} \n\n {str(e)}")
