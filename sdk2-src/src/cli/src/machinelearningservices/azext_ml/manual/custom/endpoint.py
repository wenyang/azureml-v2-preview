# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.ml.constants import ONLINE_ENDPOINT_TYPE


def ml_endpoint_show(cmd, resource_group_name, workspace_name, name, type=ONLINE_ENDPOINT_TYPE):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.get(type=type, name=name)


def ml_endpoint_create(cmd, resource_group_name, workspace_name, file, name=None, type=ONLINE_ENDPOINT_TYPE):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.create(type=type, name=name, file=file)


def ml_endpoint_delete(cmd, resource_group_name, workspace_name, name, deployment=None, type=ONLINE_ENDPOINT_TYPE):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.delete(type=type, name=name, deployment=deployment)


def ml_endpoint_get_deployment_logs(
    cmd, resource_group_name, workspace_name, name, deployment, tail, type=ONLINE_ENDPOINT_TYPE, container=None
):
    subscription_id = get_subscription_id(cmd.cli_ctx)
    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.get_deployment_logs(
        type=type, endpoint_name=name, deployment_name=deployment, tail=tail, container_type=container
    )


def ml_endpoint_listkeys(cmd, resource_group_name, workspace_name, name, type=ONLINE_ENDPOINT_TYPE):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.list_keys(type=type, name=name)


def ml_endpoint_list(cmd, resource_group_name, workspace_name, type=ONLINE_ENDPOINT_TYPE):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        default_workspace_name=workspace_name,
        credential=AzureCliCredential(),
    )
    return ml_client.endpoints.list(type=type)
