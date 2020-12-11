# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    ManagedIdentityCredential,
    SharedTokenCacheCredential,
    EnvironmentCredential,
    InteractiveBrowserCredential,
)

from azure.ml.constants import MFE_BASE_URL, OperationTypes
from azure.ml._operations import (
    ComputeOperations,
    DatastoreOperations,
    JobOperations,
    WorkspaceOperations,
    ModelOperations,
    DataOperations,
    CodeOperations,
    EnvironmentOperations,
)
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import (
    AzureMachineLearningWorkspaces,
)
from azure.ml._workspace_dependent_operations import WorkspaceScope, OperationsContainer
from azure.ml._utils.utils import _get_developer_override
from azure.ml._operations import EndpointOperations


class MLClient(object):
    def __init__(
        self,
        subscription_id: str,
        resource_group_name: str,
        default_workspace_name: str = None,
        base_url: str = MFE_BASE_URL,
        credential: ChainedTokenCredential = None,
    ):
        base_url, enforce_https = _get_developer_override(base_url)
        kwargs = {"enforce_https": enforce_https}

        self._workspace_scope = WorkspaceScope(subscription_id, resource_group_name, default_workspace_name)

        if credential:
            self._credential = credential
        else:
            self._credential = self._default_chained_credentials()

        self._service_client = AzureMachineLearningWorkspaces(
            subscription_id=self._workspace_scope._subscription_id, credential=self._credential, base_url=base_url
        )

        self._operation_container = OperationsContainer()
        self._datastores = DatastoreOperations(self._workspace_scope, self._service_client, **kwargs)
        self._workspaces = WorkspaceOperations(self._workspace_scope, self._service_client)
        self._computes = ComputeOperations(self._workspace_scope, self._service_client)
        self._model = ModelOperations(self._workspace_scope, self._service_client, self._datastores)
        self._endpoints = EndpointOperations(
            self._workspace_scope, self._service_client, self._operation_container, self._credential, **kwargs
        )
        self._data = DataOperations(self._workspace_scope, self._service_client, self._datastores, **kwargs)
        self._code = CodeOperations(self._workspace_scope, self._service_client, self._datastores, **kwargs)
        self._environments = EnvironmentOperations(self._workspace_scope, self._service_client, **kwargs)
        self._jobs = JobOperations(self._workspace_scope, self._service_client, self._operation_container, **kwargs)

        self._operation_container.add(OperationTypes.WORKSPACES, self._workspaces)
        self._operation_container.add(OperationTypes.COMPUTES, self._computes)
        self._operation_container.add(OperationTypes.DATASTORES, self._datastores)
        self._operation_container.add(OperationTypes.MODELS, self._model)
        self._operation_container.add(OperationTypes.ENDPOINTS, self._endpoints)
        self._operation_container.add(OperationTypes.DATASETS, self._data)
        self._operation_container.add(OperationTypes.CODES, self._code)
        self._operation_container.add(OperationTypes.JOBS, self._jobs)
        self._operation_container.add(OperationTypes.ENVIRONMENTS, self._environments)

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
    def data(self) -> DataOperations:
        return self._data

    @property
    def endpoints(self) -> EndpointOperations:
        return self._endpoints

    @property
    def code(self) -> CodeOperations:
        return self._code

    @property
    def default_workspace_name(self) -> Optional[str]:
        return self._workspace_scope.workspace_name

    @property
    def datastores(self) -> DatastoreOperations:
        return self._datastores

    @property
    def environments(self) -> EnvironmentOperations:
        return self._environments

    @default_workspace_name.setter
    def default_workspace_name(self, value: str) -> None:
        self._workspace_scope.workspace_name = value

    def _default_chained_credentials(self) -> ChainedTokenCredential:
        managed_identity = ManagedIdentityCredential()
        azure_cli = AzureCliCredential()
        environment = EnvironmentCredential()
        shared_token_cache = SharedTokenCacheCredential()
        interactive_browser = InteractiveBrowserCredential()

        return ChainedTokenCredential(managed_identity, azure_cli, environment, shared_token_cache, interactive_browser)
