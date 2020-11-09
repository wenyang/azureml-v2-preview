from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations.data_operations import DataOperations, DatastoreOperations
import pytest
from unittest.mock import Mock
from azure.ml import MLClient
from constants import Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version

@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)

@pytest.fixture
def mock_data_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock) -> DataOperations:
    yield DataOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, datastore_operations=mock_datastore_operation)


class TestDataOperations():
    def test_list(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        mock_data_operations.list(name_only)
        mock_data_operations._operation.list.assert_called_once_with(name_only, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

        version = "1.2"
        mock_data_operations.list("{}:{}".format(name_only, version))
        mock_data_operations._operation.get.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_get(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        mock_data_operations.get(name_only)
        mock_data_operations._operation.get.assert_called_once_with(name_only, "1", Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_get_version(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        version = "1.2"
        mock_data_operations.get("{}:{}".format(name_only, version))
        mock_data_operations._operation.get.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_create(self, mock_data_operations: DataOperations, randstr: str) -> None:
        mock_data_operations.create(name=randstr)
        mock_data_operations._operation.create_or_update.assert_called_once()

    def test_delete(self, mock_data_operations: DataOperations) -> None:
        name_only = "some_name"
        with pytest.raises(Exception):
            mock_data_operations.delete(name_only)

        version = "1.2"
        mock_data_operations.delete("{}:{}".format(name_only, version))
        mock_data_operations._operation.delete.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)
