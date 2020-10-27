# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id


def ml_dataset_list(cmd,
                    subscription_id,
                    resource_group_name,
                    workspace_name,
                    name):
    # TODO: add subscription None check for all commands
    subscription_id = subscription_id or get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.datasets.list(name=name)


def ml_dataset_show(cmd,
                    subscription_id,
                    resource_group_name,
                    workspace_name,
                    name):
    # TODO: add subscription None check for all commands
    subscription_id = subscription_id or get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.datasets.get(name=name)


def ml_dataset_create(cmd,
                      subscription_id,
                      resource_group_name,
                      workspace_name,
                      name=None,
                      description=None,
                      file=None):
    # TODO: add subscription None check for all commands
    subscription_id = subscription_id or get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.datasets.create(name=name, description=description, file=file)


def ml_dataset_delete(cmd,
                      subscription_id,
                      resource_group_name,
                      workspace_name,
                      name):
    # TODO: add subscription None check for all commands
    subscription_id = subscription_id or get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.datasets.delete(name=name)
