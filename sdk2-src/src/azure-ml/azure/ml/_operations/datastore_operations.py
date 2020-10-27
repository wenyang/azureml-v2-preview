# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Iterable

from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW
from azure.ml._datastore.datastore_utilities import create_azure_blob_storage_request
from azure.ml._restclient.machinelearningservices._azure_machine_learning_workspaces import AzureMachineLearningWorkspaces
from azure.ml._restclient.machinelearningservices.models import DatastoreCredentials, \
    DatastorePropertiesResource, DatastorePropertiesResourceArmPaginatedResult
from azure.ml._workspace_dependent_operations import WorkspaceScope, _WorkspaceDependentOperations


class DatastoreOperations(_WorkspaceDependentOperations):
    """Represents a client for performing operations on Datastores

    You should not instantiate this class directly. Instead, you should create MLClient and
    use this client via the property MLClient.datastores
    """

    def __init__(self, workspace_scope: WorkspaceScope, service_client: AzureMachineLearningWorkspaces):
        super(DatastoreOperations, self).__init__(workspace_scope)
        self._operation = service_client.datastores

    def list(self, include_secrets: bool = False) -> Iterable[DatastorePropertiesResourceArmPaginatedResult]:
        """Lists all datastores and associated information within a workspace
        """
        ds_list = list(self._operation.list(self._workspace_scope.subscription_id,
                                            self._workspace_scope.resource_group_name,
                                            self._workspace_name,
                                            api_version=API_VERSION_2020_09_01_PREVIEW))
        # TODO: remove this when service side allows getting secrets directly through list
        if include_secrets:
            for ds in ds_list:
                ds_credentials = self._list_secrets(ds.name)  # type: ignore
                if ds.properties.contents.azure_storage:  # type: ignore
                    ds.properties.contents.azure_storage.credentials = ds_credentials  # type: ignore
        return ds_list

    def _list_secrets(self, datastore_name: str) -> DatastoreCredentials:
        return self._operation.list_secrets(datastore_name,
                                            self._workspace_scope.subscription_id,
                                            self._workspace_scope.resource_group_name,
                                            self._workspace_name,
                                            api_version=API_VERSION_2020_09_01_PREVIEW)

    def delete(self, datastore_name: str) -> None:
        """Deletes a datastore reference with the given name from the workspace. This method
        does not delete the actual datastore or underlying data in the datastore.
        """
        return self._operation.delete(datastore_name,
                                      self._workspace_scope.subscription_id,
                                      self._workspace_scope.resource_group_name,
                                      self._workspace_name,
                                      api_version=API_VERSION_2020_09_01_PREVIEW)

    def show(self, datastore_name: str, include_secrets: bool = False) -> DatastorePropertiesResource:
        """Returns information about the datastore referenced by the given name
        """
        datastore_properties = self._operation.get(datastore_name,
                                                   self._workspace_scope.subscription_id,
                                                   self._workspace_scope.resource_group_name,
                                                   self._workspace_name,
                                                   api_version=API_VERSION_2020_09_01_PREVIEW)
        # TODO: remove this when services allow getting secrets with just _operation.get
        if include_secrets:
            if datastore_properties.name:
                datastore_credentials = self._list_secrets(datastore_properties.name)
                if datastore_properties.properties.contents.azure_storage:
                    datastore_properties.properties.contents.azure_storage.credentials = datastore_credentials
        return datastore_properties

    def get_default(self, include_secrets: bool = False) -> DatastorePropertiesResource:
        ds = self._operation.list(self._workspace_scope.subscription_id,
                                  self._workspace_scope.resource_group_name,
                                  self._workspace_name,
                                  is_default=True,
                                  api_version=API_VERSION_2020_09_01_PREVIEW).next()
        if include_secrets:
            ds_secret = self._list_secrets(ds.name)  # type: ignore
            if ds.properties.contents.azure_storage:
                ds.properties.contents.azure_storage.credentials = ds_secret
        return ds

    def attach_azure_blob_storage(self, datastore_name: str, container_name: str, account_name: str, description: str = None,
                                  has_been_validated: bool = None, ident: str = None, is_default: bool = None,
                                  tags: Dict[str, str] = None, sas_token: str = None, account_key: str = None, protocol: str = None,
                                  endpoint: str = None, blob_cache_timeout: str = None) -> DatastorePropertiesResource:
        """Registers an Azure Blob container to the workspace

        You can use either a SAS Token or Storage Account Key as a credential to the datastore.
        """
        request_body = create_azure_blob_storage_request(container_name,
                                                         account_name,
                                                         description=description,
                                                         has_been_validated=has_been_validated,
                                                         ident=ident,
                                                         is_default=is_default,
                                                         tags=tags,
                                                         sas_token=sas_token,
                                                         account_key=account_key,
                                                         protocol=protocol,
                                                         endpoint=endpoint,
                                                         blob_cache_timeout=blob_cache_timeout)
        return self._operation.create_or_update(datastore_name,
                                                self._workspace_scope.subscription_id,
                                                self._workspace_scope.resource_group_name,
                                                self._workspace_name,
                                                request_body,
                                                api_version=API_VERSION_2020_09_01_PREVIEW)
