import os
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations import OnlineEndpointDeploymentOperations
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.identity import DefaultAzureCredential
from azure.ml import MLClient
from utilities.utils import write_script

@pytest.fixture
def mock_endpoint_deployment_operations(mock_workspace_scope: WorkspaceScope,
                                        mock_aml_services: Mock) -> OnlineEndpointDeploymentOperations:
    yield OnlineEndpointDeploymentOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def create_endpoint_deployment_yaml_no_endpoint(tmp_path: str) -> str:
    deployment_create_yaml = """
{
    "location": "centraluseuap",
    "name": "bluedeployment",
    "sub_type": "online",
    "model": "modelid",
    "code": "codeid",
    "environment": "environmentid",
    "compute_type": "AMLCompute",
    "instance_count": 2
}
"""
    return write_script(os.path.join(tmp_path, "create_endpoint.yml"), deployment_create_yaml)


class TestOnlineEndpointDeploymentOperations:
    def test_list(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations,
                  randstr: str) -> None:
        mock_endpoint_deployment_operations.list_by_endpoint(endpoint_name=randstr)
        mock_endpoint_deployment_operations._operation.list_by_inference_endpoint.assert_called_once()

    def test_get(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations, randstr: str) -> None:
        mock_endpoint_deployment_operations.get(endpoint_name=randstr,
                                                name=randstr)
        mock_endpoint_deployment_operations._operation.get.assert_called_once()

    def test_delete(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations, randstr: str) -> None:
        mock_endpoint_deployment_operations.delete(endpoint_name=randstr,
                                                   name=randstr)
        mock_endpoint_deployment_operations._operation.delete.assert_called_once()

    def test_create_or_update(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations,
                              randstr: str) -> None:
        create_endpoint_deployment_yaml = "tests/test_configs/online_endpoint_deployment_create.yaml"
        mock_endpoint_deployment_operations.create_or_update(name=randstr, file=create_endpoint_deployment_yaml)
        mock_endpoint_deployment_operations._operation.create_or_update.assert_called_once()

    def test_create_or_update_no_file_throw_exception(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_deployment_operations.create_or_update(name=randstr)
    
    def test_create_or_update_no_name_throw_exception(self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_deployment_operations.create_or_update()
    
    def test_create_or_update_no_endpoint_throw_exception(
            self, mock_endpoint_deployment_operations: OnlineEndpointDeploymentOperations, 
            randstr: str, create_endpoint_deployment_yaml_no_endpoint: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_deployment_operations.create_or_update(
                name=randstr, file=create_endpoint_deployment_yaml_no_endpoint)