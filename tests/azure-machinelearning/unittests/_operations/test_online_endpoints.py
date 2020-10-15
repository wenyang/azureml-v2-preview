from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
from azure.machinelearning._operations.online_endpoint_operations import OnlineEndpointOperations
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential
from azure.machinelearning import MachineLearningClient

@pytest.fixture
def mock_online_endpoint_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> OnlineEndpointOperations:
    yield OnlineEndpointOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestOnlineEndpointsOperations:
    def test_list(self, mock_online_endpoint_operations: OnlineEndpointOperations) -> None:
        mock_online_endpoint_operations.list()
        mock_online_endpoint_operations._operation.list_online_endpoints.assert_called_once()

    def test_get(self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: str) -> None:
        mock_online_endpoint_operations.get(randstr)
        mock_online_endpoint_operations._operation.get.assert_called_once()

    def test_delete(self, mock_online_endpoint_operations: OnlineEndpointOperations, randstr: str) -> None:
        mock_online_endpoint_operations.delete(randstr)
        mock_online_endpoint_operations._operation.delete.assert_called_once()

    def test_create_or_update(self, mock_online_endpoint_operations: OnlineEndpointOperations,
                              randstr: str, create_endpoint_yaml: str) -> None:
        mock_online_endpoint_operations.create_or_update(name=randstr, file=create_endpoint_yaml)
        mock_online_endpoint_operations._operation.create_or_update.assert_called_once()

    def test_create_or_update_no_file_throw_exception(self, mock_online_endpoint_operations: OnlineEndpointOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_online_endpoint_operations.create_or_update(name=randstr)