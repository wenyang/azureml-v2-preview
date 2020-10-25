from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations import EndpointOperations
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential
from azure.ml import MLClient
from azure.ml.constants import ONLINE_ENDPOINT_TYPE, BATCH_ENDPOINT_TYPE

@pytest.fixture
def mock_endpoint_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> EndpointOperations:
    yield EndpointOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestEndpointsOperations:
    def test_online_list(self, mock_endpoint_operations: EndpointOperations) -> None:
        mock_endpoint_operations.list(type=ONLINE_ENDPOINT_TYPE)
        mock_endpoint_operations._online_operation.list_online_endpoints.assert_called_once()

    def test_online_get(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.get(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.get.assert_called_once()

    def test_online_delete(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.delete(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.delete.assert_called_once()

    def test_online_create(self, mock_endpoint_operations: EndpointOperations,
                              randstr: str) -> None:
        create_endpoint_yaml = "tests/test_configs/online_endpoint_create.yaml"
        mock_endpoint_operations.create(type=ONLINE_ENDPOINT_TYPE, name=randstr, file=create_endpoint_yaml)
        mock_endpoint_operations._online_operation.create_or_update.assert_called_once()

    def test_create_no_file_throw_exception(self, mock_endpoint_operations: EndpointOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.create(type=ONLINE_ENDPOINT_TYPE, name=randstr)
    
    def test_create_no_type_throw_exception(self, mock_endpoint_operations: EndpointOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.create(name=randstr)
    
    def test_batch_list(self, mock_endpoint_operations: EndpointOperations) -> None:
        mock_endpoint_operations.list(type=BATCH_ENDPOINT_TYPE)
        mock_endpoint_operations._batch_operation.list.assert_called_once()

    def test_batch_get(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.get(type=BATCH_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._batch_operation.get.assert_called_once()

    def test_batch_delete(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.delete(type=BATCH_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._batch_operation.delete.assert_called_once()