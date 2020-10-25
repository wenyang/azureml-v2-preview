# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def load_datastore_params(self):
    with self.argument_context('ml datastore attach-blob') as c:
        c.argument('subscription-id', help="subscription id of workspace")
        c.argument('resource-group', help="resource group of workspace")
        c.argument('workspace-name', help="workspace to which blob container will be attached")
        c.argument('account-name', help="name of storage account")
        c.argument('container-name', help="name of blob container to attach to workspace")
        c.argument('name', help="datastore name")
        c.argument('account-key', help="storage account key")
        c.argument('sas-token', help="sas token for storage account")
        c.argument('protocol', help="protocol used to connect to blob container")
        c.argument('endpoint', help="The endpoint of the storage account. Defaults to core.windows.net.")

    with self.argument_context('ml datastore detach') as c:
        c.argument('subscription-id', help="subscription id of workspace")
        c.argument('resource-group', help="resource group of workspace")
        c.argument('workspace-name', help="workspace to which blob container will be attached")
        c.argument('name', help="name of datastore to detach from workspace")

    with self.argument_context('ml datastore show') as c:
        c.argument('include-secrets', action="store_true", help="when argument present, returns secrets for datastore")

    with self.argument_context('ml datastore list') as c:
        c.argument('include-secrets', action="store_true", help="when argument present, returns secrets for datastore")
