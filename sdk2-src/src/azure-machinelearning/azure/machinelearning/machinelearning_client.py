# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.identity import DefaultAzureCredential

from azure.machinelearning.constants import MFE_BASE_URL
from azure.machinelearning._operations import ComputeOperations, DatastoreOperations, JobOperations, \
    WorkspaceOperations, ModelOperations, DatasetOperations, CodeOperations
from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
from azure.machinelearning._utils.utils import _get_developer_override
from azure.machinelearning._operations import OnlineEndpointOperations, OnlineEndpointDeploymentOperations


class MachineLearningClient(object):
    def __init__(self,
                 subscription_id: str,
                 resource_group_name: str,
                 default_workspace_name: str = None,
                 base_url: str = MFE_BASE_URL,
                 credential: DefaultAzureCredential = None):
        base_url, enforce_https = _get_developer_override(base_url)
        kwargs = {"enforce_https": enforce_https}

        self._workspace_scope = WorkspaceScope(subscription_id, resource_group_name, default_workspace_name)

        self._credential = credential if credential else DefaultAzureCredential(
            exclude_interactive_browser_credential=False, exclude_visual_studio_code_credential=True)

        self._service_client = AzureMachineLearningWorkspaces(subscription_id=self._workspace_scope._subscription_id,
                                                              credential=self._credential,
                                                              base_url=base_url)

        self._workspaces = WorkspaceOperations(self._workspace_scope, self._service_client)
        self._jobs = JobOperations(self._workspace_scope, self._service_client, self._workspaces, **kwargs)
        self._computes = ComputeOperations(self._workspace_scope, self._service_client)
        self._model = ModelOperations(self._workspace_scope, self._service_client)
        self._online_endpoints = OnlineEndpointOperations(self._workspace_scope, self._service_client)
        self._online_endpoint_deployments = OnlineEndpointDeploymentOperations(self._workspace_scope, self._service_client)
        self._datastores = DatastoreOperations(self._workspace_scope, self._service_client)
        self._datasets = DatasetOperations(self._workspace_scope, self._service_client)
        self._code_assets = CodeOperations(self._workspace_scope, self._service_client)

    @property
    def workspaces(self) -> WorkspaceOperations:
        return self._workspaces

    @property
    def jobs(self) -> JobOperations:
        return self._jobs

    @property
    def computes(self) -> ComputeOperations:
        return self._computes

    @property
    def model(self) -> ModelOperations:
        return self._model

    @property
    def datasets(self) -> DatasetOperations:
        return self._datasets

    @property
    def online_endpoints(self) -> OnlineEndpointOperations:
        return self._online_endpoints

    @property
    def online_endpoint_deployments(self) -> OnlineEndpointDeploymentOperations:
        return self._online_endpoint_deployments

    @property
    def code_assets(self) -> CodeOperations:
        return self._code_assets

    @property
    def default_workspace_name(self) -> Optional[str]:
        return self._workspace_scope.workspace_name

    @property
    def datastores(self) -> DatastoreOperations:
        return self._datastores

    @default_workspace_name.setter
    def default_workspace_name(self, value: str) -> None:
        self._workspace_scope.workspace_name = value
