# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.machinelearning import MachineLearningClient
from azure.identity import AzureCliCredential
from azure.cli.core.commands.client_factory import get_subscription_id


def ml_endpoint_show(cmd,
                     subscription_id,
                     resource_group_name,
                     workspace_name,
                     name):
    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MachineLearningClient(subscription_id=subscription_id,
                                      resource_group_name=resource_group_name,
                                      default_workspace_name=workspace_name,
                                      credential=AzureCliCredential())
    return ml_client._online_endpoints.get(name=name)


def ml_endpoint_create(cmd,
                       resource_group_name,
                       workspace_name,
                       name,
                       properties=None,
                       file=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    ml_client = MachineLearningClient(subscription_id=subscription_id,
                                      resource_group_name=resource_group_name,
                                      default_workspace_name=workspace_name,
                                      credential=AzureCliCredential())

    return ml_client.online_endpoints.create_or_update(name=name, file=file)
