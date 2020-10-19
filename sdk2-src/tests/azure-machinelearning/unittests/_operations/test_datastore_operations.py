import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
from azure.machinelearning._operations import DatastoreOperations


@pytest.fixture
def datastore_name() -> str:
    return "test_datastore"


@pytest.fixture
def azure_storage_account_name() -> str:
    return "test_azure_storage_account"


@pytest.fixture
def azure_storage_container_name() -> str:
    return "test_azure_storage_container"


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestDatastoreOperations:
    def test_list(self, mock_datastore_operation: DatastoreOperations) -> None:
        result = mock_datastore_operation.list()
        mock_datastore_operation._operation.list.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_list_with_secrets(self, mock_datastore_operation: DatastoreOperations) -> None:
        mock_datastore_operation._operation.list.return_value = [Mock() for _ in range(5)]
        mock_datastore_operation.list(include_secrets=True)
        mock_datastore_operation._operation.list.assert_called_once()
        assert mock_datastore_operation._operation.list_secrets.call_count == 5

    def test_delete(self, mock_datastore_operation: DatastoreOperations, randstr: str) -> None:
        mock_datastore_operation.delete(randstr)
        mock_datastore_operation._operation.delete.assert_called_once()

    def test_show_no_secrets(self, mock_datastore_operation: DatastoreOperations, randstr: str) -> None:
        mock_datastore_operation.show(randstr)
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_not_called()

    def test_show_no_secrets(self, mock_datastore_operation: DatastoreOperations, randstr: str) -> None:
        mock_datastore_operation.show(randstr, include_secrets=True)
        mock_datastore_operation._operation.get.assert_called_once()
        mock_datastore_operation._operation.list_secrets.assert_called_once()

    def test_attach_azure_blob_storage(self, mock_datastore_operation: DatastoreOperations, datastore_name: str,
                                       azure_storage_account_name: str, azure_storage_container_name: str) -> None:
        mock_datastore_operation.attach_azure_blob_storage(datastore_name, azure_storage_container_name,
                                                           azure_storage_account_name)
        mock_datastore_operation._operation.create_or_update.assert_called_once()
