# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml._workspace_dependent_operations import WorkspaceScope

DATASTORE_RESOURCE_ID = "/subscriptions/{}/resourceGroups/{}/providers/" \
                        "Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"


def get_datastore_arm_id(datastore_name: str, workspace_scope: WorkspaceScope) -> str:
    return DATASTORE_RESOURCE_ID.format(workspace_scope.subscription_id,
                                        workspace_scope.resource_group_name,
                                        workspace_scope.workspace_name,
                                        datastore_name)
