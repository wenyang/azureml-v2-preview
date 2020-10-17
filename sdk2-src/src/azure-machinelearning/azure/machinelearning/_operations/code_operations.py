# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Union, cast, Optional

from azure.machinelearning._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope
from azure.machinelearning._operations import WorkspaceOperations
from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import CodeVersionResource, CodeVersion, \
    CodeContainer, CodeContainerResource
import azure.machinelearning._artifacts._artifact_utilities as artifact_utils
from azure.machinelearning.constants import API_VERSION_2020_09_01_PREVIEW
from azureml.core import Datastore


class CodeOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(CodeOperations, self).__init__(workspace_scope)
        self._service_client = service_client
        self._version_operation = service_client.code_versions
        self._container_operation = service_client.code_containers

    def create(self, name: str, directory: Union[str, os.PathLike], version: str = None,
               datastore_name: Optional[str] = None, show_progress: bool = True) -> CodeVersionResource:

        workspace = WorkspaceOperations(self._workspace_scope, self._service_client).get(self._workspace_name)

        if not datastore_name:
            datastore = workspace.get_default_datastore()
        else:
            datastore = Datastore.get(workspace, datastore_name)

        remote_path, resource_id = artifact_utils.upload_artifact(local_path=directory,
                                                                  datastore=datastore,
                                                                  show_progress=show_progress)
        if resource_id:
            resource_id.format(self._workspace_scope.subscription_id, self._workspace_scope.resource_group_name)

        code_container_resource = CodeContainerResource(name=name, properties=CodeContainer())
        self._container_operation.create_or_update(name=name,
                                                   subscription_id=self._workspace_scope.subscription_id,
                                                   resource_group_name=self._workspace_scope.resource_group_name,
                                                   workspace_name=self._workspace_name,
                                                   body=code_container_resource,
                                                   api_version=API_VERSION_2020_09_01_PREVIEW)

        code_version = CodeVersion(asset_paths=remote_path, datastore_id=resource_id)
        code_version_resource = CodeVersionResource(properties=code_version)
        if not version:
            version = self._version_gen()
        return self._version_operation.create_or_update(name=name, version=version,
                                                        subscription_id=self._workspace_scope.subscription_id,
                                                        resource_group_name=self._workspace_scope.resource_group_name,
                                                        workspace_name=self._workspace_name,
                                                        body=code_version_resource,
                                                        api_version=API_VERSION_2020_09_01_PREVIEW)

    def show(self, name: str) -> CodeVersionResource:
        name, version = name.split(':') if ":" in name else (name, None)

        if not version:
            for code_version in self._version_operation.list(
                    name=name, subscription_id=self._workspace_scope.subscription_id,
                    resource_group_name=self._workspace_scope.resource_group_name,
                    workspace_name=self._workspace_name,
                    api_version='2020-09-01-preview',
                    latest_version_only=True):
                return cast(CodeVersionResource, code_version)
            raise Exception(f"No code versions for code asset: {name}")
        else:
            return self._version_operation.get(
                name=name,
                version=version,
                subscription_id=self._workspace_scope.subscription_id,
                resource_group_name=self._workspace_scope.resource_group_name,
                workspace_name=self._workspace_name,
                api_version='2020-09-01-preview',
            )

    def _version_gen(self) -> str:
        # TODO: implement the real version generator
        return "1"
