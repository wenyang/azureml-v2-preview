# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id


def ml_data_list(cmd,
                 resource_group_name,
                 workspace_name,
                 name=None):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.data.list(name=name)


def ml_data_show(cmd,
                 resource_group_name,
                 workspace_name,
                 name,
                 version):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.data.get(name=name, version=version)


def ml_data_create(cmd,
                   resource_group_name,
                   workspace_name,
                   name=None,
                   version=None,
                   file=None):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.data.create_or_update(name=name, version=version, yaml_path=file)


def ml_data_update(cmd,
                   resource_group_name,
                   workspace_name,
                   name=None,
                   version=None,
                   description=None,
                   file=None):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.data.create_or_update(name=name, version=version, description=description, yaml_path=file)


def ml_data_upload(cmd,
                   resource_group_name,
                   workspace_name,
                   name,
                   version,
                   path,
                   datastore=None,
                   description=None):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    return ml_client.data.upload(name=name, version=version, description=description, local_path=path, linked_service_name=datastore)


def ml_data_delete(cmd,
                   resource_group_name,
                   workspace_name,
                   name,
                   version):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.data.delete(name=name, version=version)
