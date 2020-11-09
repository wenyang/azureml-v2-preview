# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Iterable

from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import ComputeResource, PaginatedComputeResourcesList
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope


class ComputeOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(ComputeOperations, self).__init__(workspace_scope)
        self._operation = service_client.machine_learning_compute

    def list(self) -> Iterable[PaginatedComputeResourcesList]:
        return self._operation.list_by_workspace(self._workspace_scope.resource_group_name, self._workspace_name)

    def get(self, name: str) -> ComputeResource:
        return self._operation.get(self._workspace_scope.resource_group_name, self._workspace_name, name)
