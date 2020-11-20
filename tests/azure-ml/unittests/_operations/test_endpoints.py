import os
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations import EndpointOperations, CodeOperations, ModelOperations, DatastoreOperations, EnvironmentOperations
import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from azure.identity import DefaultAzureCredential
from azure.ml import MLClient
from azure.ml.constants import ONLINE_ENDPOINT_TYPE, BATCH_ENDPOINT_TYPE
from azure.ml._restclient.machinelearningservices.models import (
    OnlineEndpointPropertiesTrackedResource, OnlineEndpointProperties, AuthKeys, AuthToken, AksComputeConfiguration)
from utilities.utils import write_script

@pytest.fixture
def create_yaml_no_type(tmp_path) -> str:
    content = """
        location: centraluseuap
        name: myendpoint
        compute_type: AMLCompute
        auth_mode: AMLTokenAuth
        #infrastructure: vc:xyz-slice-of-managed-quota #(proposed experience once vc concept lands)
        traffic:
            blue: 0
    """
    return write_script(os.path.join(tmp_path, "create_no_type.yaml"), content)

@pytest.fixture
def create_yaml_happy_path(tmp_path) -> str:
    content = """
location: centraluseuap
name: aksendpoint
infrastructure: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/endpointakstest
auth_mode: Key
traffic:
    blue: 0
deployments:
        #blue deployment
    blue:   
        model: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/models/sklearn_regression_model:1
        code_configuration:
            code:
                directory: ./endpoint
            scoring_script: ./test.py
        environment: azureml:/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/environments/AzureML-Minimal/versions/2
        sku: Standard_FS4_v2
        scale_settings:
            scale_type: manual
            instance_count: 1
            min_instances: 1
            max_instances: 1
        request_settings:
            request_timeout_ms: 3000
            max_concurrent_requests_per_instance: 1
            max_queue_wait_ms: 3000
        resource_requirements:
            cpu: 1.5
            memory: 1.0
    """
    return write_script(os.path.join(tmp_path, "create_happy_path.yaml"), content)


@pytest.fixture
def mock_datastore_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> CodeOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_model_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock,
                          mock_datastore_operations: DatastoreOperations) -> ModelOperations:
    yield ModelOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services,
                          datastore_operations=mock_datastore_operations)


@pytest.fixture
def mock_code_assets_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock,
                                mock_datastore_operations: DatastoreOperations) -> CodeOperations:
    yield CodeOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services,
                         datastore_operations=mock_datastore_operations)


@pytest.fixture
def mock_environment_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> EnvironmentOperations:
    yield EnvironmentOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_endpoint_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock,
                             mock_machinelearning_client: Mock,
                             mock_environment_operations: Mock,
                             mock_model_operations: Mock,
                             mock_code_assets_operations: Mock
                             ) -> EndpointOperations:
    mock_machinelearning_client._operation_container.add("code", mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add("model", mock_code_assets_operations)
    mock_machinelearning_client._operation_container.add("environments", mock_code_assets_operations)
    yield EndpointOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services,
                             all_operations=mock_machinelearning_client._operation_container)


class TestEndpointsOperations:
    def test_online_list(self, mock_endpoint_operations: EndpointOperations) -> None:
        mock_endpoint_operations.list(type=ONLINE_ENDPOINT_TYPE)
        mock_endpoint_operations._online_operation.list.assert_called_once()

    def test_throw_if_random_type(self, mock_endpoint_operations: EndpointOperations) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.list(type="test_type")

    def test_online_get(self, mock_endpoint_operations: EndpointOperations, randstr: str, mock_aml_services: Mock) -> None:
        mock_aml_services.online_endpoints.get.return_value = OnlineEndpointPropertiesTrackedResource(
                name=randstr, properties=OnlineEndpointProperties(
                    compute_configuration=AksComputeConfiguration(compute_name="compute"),
                    auth_mode="key"))
        mock_aml_services.online_deployments.list_by_inference_endpoint.return_value = None
        mock_endpoint_operations.get(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.get.assert_called_once()
        mock_endpoint_operations._online_deployment.list_by_inference_endpoint.assert_called_once()

    def test_online_list_keys(self,
                              mock_endpoint_operations: EndpointOperations,
                              randstr: str,
                              mock_aml_services: Mock) -> None:
        mock_aml_services.online_endpoints.get.return_value = OnlineEndpointPropertiesTrackedResource(
                name=randstr, properties=OnlineEndpointProperties(
                    auth_mode="key"
                ))
        mock_endpoint_operations.list_keys(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.get.assert_called_once()
        mock_endpoint_operations._online_operation.list_keys.assert_called_once()

    def test_online_list_token(self,
                               mock_endpoint_operations: EndpointOperations,
                               randstr: str,
                               mock_aml_services: Mock,) -> None:
        mock_aml_services.online_endpoints.get.return_value = OnlineEndpointPropertiesTrackedResource(
                name=randstr, properties=OnlineEndpointProperties(
                    auth_mode="amltoken"
                ))
        mock_endpoint_operations.list_keys(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.get.assert_called_once()
        mock_endpoint_operations._online_operation.get_token.assert_called_once()

    def test_online_delete(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.delete(type=ONLINE_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._online_operation.delete.assert_called_once()

    def test_online_create(self,
                           mock_endpoint_operations: EndpointOperations,
                           randstr: str,
                           create_yaml_happy_path: str,
                           mocker: MockFixture) -> None:
        mocker.patch("azure.ml._operations.endpoint_operations.OperationOrchestrator.get_code_asset_arm_id",
                     return_value="xxx")
        mocker.patch("azure.ml._operations.endpoint_operations.OperationOrchestrator.get_environment_arm_id",
                     return_value="xxx")
        mocker.patch("azure.ml._operations.endpoint_operations.OperationOrchestrator.get_model_arm_id",
                     return_value="xxx")
        mock_endpoint_operations.create(type=ONLINE_ENDPOINT_TYPE, name=randstr, file=create_yaml_happy_path)
        assert mock_endpoint_operations._online_operation.create_or_update.call_count == 2
        mock_endpoint_operations._online_deployment.create_or_update.assert_called_once()

    def test_create_no_file_throw_exception(self, mock_endpoint_operations: EndpointOperations, 
                                                      randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.create(type=ONLINE_ENDPOINT_TYPE, name=randstr, file=None)

    def test_create_no_type_throw_exception(self, mock_endpoint_operations: EndpointOperations, 
                                            randstr: str) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.create(name=randstr, file=None)

    def test_create_no_type_in_file_throw_exception(self, mock_endpoint_operations: EndpointOperations, 
                                                    randstr: str,
                                                    create_yaml_no_type) -> None:
        with pytest.raises(Exception):
            mock_endpoint_operations.create(name=randstr, file=None)

    def test_batch_list(self, mock_endpoint_operations: EndpointOperations) -> None:
        mock_endpoint_operations.list(type=BATCH_ENDPOINT_TYPE)
        mock_endpoint_operations._batch_operation.list.assert_called_once()

    def test_batch_get(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.get(type=BATCH_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._batch_operation.get.assert_called_once()

    def test_batch_delete(self, mock_endpoint_operations: EndpointOperations, randstr: str) -> None:
        mock_endpoint_operations.delete(type=BATCH_ENDPOINT_TYPE, name=randstr)
        mock_endpoint_operations._batch_operation.delete.assert_called_once()