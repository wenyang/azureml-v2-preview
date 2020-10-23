# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml import MLClient
from azure.identity import AzureCliCredential


def ml_datastore_attach_blob(cmd,
                             subscription_id,
                             resource_group_name,
                             workspace_name,
                             account_name,
                             container_name,
                             name,
                             account_key=None,
                             sas_token=None,
                             protocol=None,
                             endpoint=None):

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())

    return ml_client.datastores.attach_azure_blob_storage(name,
                                                          container_name,
                                                          account_name,
                                                          account_key=account_key,
                                                          sas_token=sas_token,
                                                          protocol=protocol,
                                                          endpoint=endpoint)


def ml_datastore_detach(cmd,
                        subscription_id,
                        resource_group_name,
                        workspace_name,
                        datastore_name):

    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name,
                         credential=AzureCliCredential())
    return ml_client.datastores.delete(datastore_name)


def ml_datastore_show(cmd,
                      subscription_id,
                      resource_group_name,
                      workspace_name,
                      datastore_name,
                      include_secrets=False):
    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name)
    return ml_client.datastores.show(datastore_name, include_secrets=include_secrets)


def ml_datastore_list(client,
                      subscription_id,
                      resource_group_name,
                      workspace_name,
                      include_secrets=False,
                      skip_token=None,
                      count=None,
                      is_default=None,
                      names=None,
                      search_text=None,
                      order_by=None,
                      order_by_asc=None):
    ml_client = MLClient(subscription_id=subscription_id,
                         resource_group_name=resource_group_name,
                         default_workspace_name=workspace_name)
    return ml_client.datastores.list(include_secrets=include_secrets)
