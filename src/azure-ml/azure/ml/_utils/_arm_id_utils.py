# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Tuple, Any
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml.constants import ARM_ID_FULL_PREFIX

DATASTORE_RESOURCE_ID = (
    "/subscriptions/{}/resourceGroups/{}/providers/" "Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"
)
PROVIDER_RESOURCE_ID_WITH_VERSION = (
    "/subscriptions/{}/resourceGroups/{}/providers/" "Microsoft.MachineLearningServices/workspaces/{}/{}/{}/versions/{}"
)


def get_datastore_arm_id(datastore_name: str, workspace_scope: WorkspaceScope) -> str:
    return DATASTORE_RESOURCE_ID.format(
        workspace_scope.subscription_id,
        workspace_scope.resource_group_name,
        workspace_scope.workspace_name,
        datastore_name,
    )


def parse_name_version(name: str) -> Tuple[str, Optional[str]]:
    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    else:
        *name, version = token_list  # type: ignore
        return ":".join(name), version


def is_arm_id(name: Any) -> bool:
    if isinstance(name, str) and name.startswith(ARM_ID_FULL_PREFIX):
        return True
    else:
        return False


def get_arm_id_with_version(
    workspace_scope: WorkspaceScope, provider_name: str, provider_value: str, provider_version: str
):
    return PROVIDER_RESOURCE_ID_WITH_VERSION.format(
        workspace_scope.subscription_id,
        workspace_scope.resource_group_name,
        workspace_scope.workspace_name,
        provider_name,
        provider_value,
        provider_version,
    )
