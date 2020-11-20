# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id

from .print_error import print_error
from pprint import pprint


def ml_model_create(cmd, resource_group_name, workspace_name, name=None, version=None, file=None, path=None, params_override=[]):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    if name is not None:
        params_override.append({'name': name})
    if version is not None:
        params_override.append({'version': version})
    if path is not None:
        params_override.append({'asset_path': path})
    try:
        pprint(f"parameters being override: {params_override}")
        return ml_client.model.create(file=file, params_override=params_override)
    except Exception as err:
        print_error(str(err))


def ml_model_show(cmd, resource_group_name, workspace_name, name, version):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    return ml_client.model.show(name=name, version=version)


def ml_model_list(cmd, resource_group_name, workspace_name, name=None):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    return ml_client.model.list(name=name)
