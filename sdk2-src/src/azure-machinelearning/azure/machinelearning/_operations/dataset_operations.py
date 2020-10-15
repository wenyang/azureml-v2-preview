# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import DataVersionResource, DataVersion, AssetPath, \
    DataVersionResourceArmPaginatedResult

from azure.machinelearning._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.machinelearning.constants import API_VERSION_2020_09_01_PREVIEW

from typing import Iterable


class DatasetOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(DatasetOperations, self).__init__(workspace_scope)
        self._operation = service_client.data_version

    def list(self, name: str = None) -> Iterable[DataVersionResourceArmPaginatedResult]:
        name, version = self._parse_name_version(name)

        if version:
            return self.get("{}:{}".format(name, version))
        else:
            return self._operation.list(name, self._subscription_id, self._resource_group_name, self._workspace_name, API_VERSION_2020_09_01_PREVIEW)

    def get(self, name: str = None) -> DataVersionResource:
        name, version = self._parse_name_version(name)
        if version is None:
            # TODO: get the latest version instead of the version 1
            version = "1"

        return self._operation.get(name, version, self._subscription_id, self._resource_group_name, self._workspace_name, API_VERSION_2020_09_01_PREVIEW)

    def create(self,
               name: str = None,
               description: str = None,
               datastore_id: str = None,
               datastore_path: str = None,
               is_directory: bool = False) -> DataVersionResource:
        name, version = self._parse_name_version(name)

        asset_path = AssetPath(path=datastore_path, is_directory=is_directory)

        dataset_version = DataVersion(dataset_type="simple", description=description, asset_paths=[asset_path])

        data_resource = DataVersionResource(properties=dataset_version)

        return self._operation.create_or_update(name, version, self._subscription_id, self._resource_group_name, self._workspace_name, data_resource)

    def update(self, name: str = None) -> None:
        raise Exception("Not implemented.")

    def delete(self, name: str = None) -> None:
        name, version = self._parse_name_version(name)
        if version:
            return self._operation.delete(name, version, self._subscription_id, self._resource_group_name, self._workspace_name, API_VERSION_2020_09_01_PREVIEW)
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
