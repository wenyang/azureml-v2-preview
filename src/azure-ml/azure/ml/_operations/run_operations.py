# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import RunDetailsDto
from azure.ml._workspace_dependent_operations import _WorkspaceDependentOperations, WorkspaceScope


class RunOperations(_WorkspaceDependentOperations):
    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(RunOperations, self).__init__(workspace_scope)
        self._operation = service_client.run

    def get_run_details(self, exp_name: str, run_id: str) -> RunDetailsDto:
        return self._operation.get_details(
            self._workspace_scope.subscription_id,
            self._workspace_scope.resource_group_name,
            self._workspace_name,
            exp_name,
            run_id)
