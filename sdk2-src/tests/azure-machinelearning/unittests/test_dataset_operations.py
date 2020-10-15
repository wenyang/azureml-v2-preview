from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
from azure.machinelearning._operations.dataset_operations import DatasetOperations
import pytest
from unittest.mock import Mock
from azure.machinelearning import MachineLearningClient
from constants import Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version


@pytest.fixture
def mock_dataset_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatasetOperations:
    yield DatasetOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestDatasetOperations():
    def test_list(self, mock_dataset_operations: DatasetOperations) -> None:
        name_only = "some_name"
        mock_dataset_operations.list(name_only)
        mock_dataset_operations._operation.list.assert_called_once_with(name_only, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

        version = "1.2"
        mock_dataset_operations.list("{}:{}".format(name_only, version))
        mock_dataset_operations._operation.get.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_get(self, mock_dataset_operations: DatasetOperations) -> None:
        name_only = "some_name"
        mock_dataset_operations.get(name_only)
        mock_dataset_operations._operation.get.assert_called_once_with(name_only, "1", Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_get_version(self, mock_dataset_operations: DatasetOperations) -> None:
        name_only = "some_name"
        version = "1.2"
        mock_dataset_operations.get("{}:{}".format(name_only, version))
        mock_dataset_operations._operation.get.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)

    def test_create(self, mock_dataset_operations: DatasetOperations, randstr: str) -> None:
        mock_dataset_operations.create(name=randstr)
        mock_dataset_operations._operation.create_or_update.assert_called_once()

    def test_delete(self, mock_dataset_operations: DatasetOperations) -> None:
        name_only = "some_name"
        with pytest.raises(Exception):
            mock_dataset_operations.delete(name_only)

        version = "1.2"
        mock_dataset_operations.delete("{}:{}".format(name_only, version))
        mock_dataset_operations._operation.delete.assert_called_once_with(name_only, version, Test_Subscription, Test_Resource_Group, Test_Workspace_Name, Default_API_Version)
