# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

from azure.ml._restclient.machinelearningservices.models import AzureStorageSection, AccountKeySection, \
    DatastoreCredentials, DatastoreContents, DatastoreProperties, DatastorePropertiesResource, SasSection
from .constants import AZURE_BLOB_STORAGE, SAS_TOKEN, ACCOUNT_KEY, DEFAULT_ENDPOINT, HTTPS

"""Utilities to abstract the underlying Datastore autorest models from MLClient"""


def create_azure_blob_storage_request(container_name: str = None, account_name: str = None, description: str = None,
                                      has_been_validated: bool = None, ident: str = None, is_default: bool = None,
                                      tags: Dict[str, str] = None, sas_token: str = None, account_key: str=None, protocol: str=None,
                                      endpoint: str=None, blob_cache_timeout: str = None, subscription_id: str = None,
                                      resource_group: str = None) -> DatastorePropertiesResource:
    """Creates and returns a DatastorePropertiesResourceRequest in order to attach an Azure Blob Storage Account"""

    if sas_token:
        credential = _create_sas_credential(sas_token)
    elif account_key:
        credential = _create_account_key_credential(account_key)
    else:
        credential = None

    azure_storage_section = AzureStorageSection(account_name=account_name,
                                                blob_cache_timeout=blob_cache_timeout,
                                                container_name=container_name,
                                                credentials=credential,
                                                endpoint=DEFAULT_ENDPOINT if not endpoint else endpoint,
                                                protocol=HTTPS if not protocol else protocol)
    datastore_contents = DatastoreContents(type=AZURE_BLOB_STORAGE, azure_storage=azure_storage_section)
    datastore_properties = _create_datastore_properties(datastore_contents,
                                                        description=description,
                                                        has_been_validated=has_been_validated,
                                                        ident=ident,
                                                        is_default=is_default,
                                                        tags=tags)
    return DatastorePropertiesResource(properties=datastore_properties)


def _create_datastore_properties(contents: DatastoreContents, description: str = None, has_been_validated: bool = None,
                                 ident: str = None, is_default: bool = None, tags: {str} = None) -> DatastoreProperties:
    """Creates a DatastoreProperties to be sent to MFE to attach datastore"""

    return DatastoreProperties(contents=contents,
                               description=description,
                               has_been_validated=has_been_validated,
                               id=ident,
                               is_default=is_default,
                               tags=tags)


def _create_sas_credential(sas_token: str) -> DatastoreCredentials:
    """Creates a SasSection object from a SaS token to be sent to MFE for credential verification"""

    sas_credential = SasSection(sas_token=sas_token)
    return DatastoreCredentials(type=SAS_TOKEN, sas=sas_credential)


def _create_account_key_credential(account_key: str) -> DatastoreCredentials:
    """Creates an AccountKeySection from an AccountKey token to be sent to MFE for credential verification"""

    account_key_credential = AccountKeySection(key=account_key)
    return DatastoreCredentials(type=ACCOUNT_KEY, account_key=account_key_credential)
