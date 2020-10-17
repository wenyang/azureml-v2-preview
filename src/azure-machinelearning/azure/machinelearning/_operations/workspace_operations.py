# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Iterable

from azure.core.polling import LROPoller

from azure.machinelearning._restclient.machinelearningservices._azure_machine_learning_workspaces import \
    AzureMachineLearningWorkspaces
from azure.machinelearning._restclient.machinelearningservices.models import Workspace, WorkspaceListResult
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope


class WorkspaceOperations(object):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        self._workspace_scope = workspace_scope
        self._operation = service_client.workspaces

    def list(self, scope: str = "resource_group") -> Iterable[WorkspaceListResult]:
        if scope == "resource_group":
            return self._operation.list_by_resource_group(self._workspace_scope.resource_group_name)
        elif scope == "subscription":
            return self._operation.list_by_subscription()
        else:
            # TODO: log warning
            return self._operation.list_by_resource_group(self._workspace_scope.resource_group_name)

    def get(self, name: str) -> Workspace:
        return self._operation.get(self._workspace_scope.resource_group_name, name)

    # WIP, doesn't work yet
    def create_or_update(self, name: str, **kwargs: Any) -> LROPoller[Workspace]:
        if name:
            kwargs["name"] = name
        workspace = Workspace(**kwargs)
        return self._operation.begin_create_or_update(self._workspace_scope.resource_group_name, name, workspace)

    def delete(self, name: str) -> LROPoller[None]:
        return self._operation.begin_delete(self._workspace_scope.resource_group_name, name)
