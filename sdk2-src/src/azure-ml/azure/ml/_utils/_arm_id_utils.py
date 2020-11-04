# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Tuple
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml.constants import ARM_ID_PREFIX

DATASTORE_RESOURCE_ID = "/subscriptions/{}/resourceGroups/{}/providers/" \
                        "Microsoft.MachineLearningServices/workspaces/{}/datastores/{}"


def get_datastore_arm_id(datastore_name: str, workspace_scope: WorkspaceScope) -> str:
    return DATASTORE_RESOURCE_ID.format(workspace_scope.subscription_id,
                                        workspace_scope.resource_group_name,
                                        workspace_scope.workspace_name,
                                        datastore_name)


def parse_name_version(name: str) -> Tuple[str, Optional[str]]:
    token_list = name.split(':')
    if len(token_list) == 1:
        return name, None
    else:
        *name, version = token_list  # type: ignore
        return ":".join(name), version


def try_get_arm_id(field_value: str) -> Tuple[bool, str]:
    if isinstance(field_value, str) and field_value.startswith("azureml:/subscriptions/"):
        return True, field_value[len(ARM_ID_PREFIX):]
    return False, None
