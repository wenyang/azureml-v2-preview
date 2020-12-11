# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id


def ml_compute_list(cmd, resource_group_name, workspace_name):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.computes.list()


def ml_compute_show(cmd, resource_group_name, workspace_name, name):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.computes.get(name=name)
