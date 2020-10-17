from typing import Iterator
from azure.machinelearning.machinelearning_client import JobOperations, ModelOperations, WorkspaceOperations, \
    CodeOperations, WorkspaceScope

import pytest
from typing import Iterator
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from azure.identity import DefaultAzureCredential
from azure.machinelearning import MachineLearningClient
from azure.machinelearning._operations import DatastoreOperations, JobOperations, WorkspaceOperations
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)


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
def mock_workspace_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> WorkspaceOperations:
    yield WorkspaceOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_job_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> JobOperations:
    yield JobOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_code_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> CodeOperations:
    yield CodeOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_model_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> ModelOperations:
    yield ModelOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestMachineLearningClient():
    def test_get_workspaces(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.workspaces is not None

    def test_get_jobs(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.jobs is not None

    def test_get_computes(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.computes is not None

    def test_get_datastore(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.datastores is not None

    def test_get_online_endpoints(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.online_endpoints is not None

    def test_default_workspace_name_match(self, mock_machinelearning_client: MachineLearningClient) -> None:
        assert mock_machinelearning_client.default_workspace_name is not None

    def test_set_default_workspace_name(self, mock_machinelearning_client: MachineLearningClient) -> None:
        default_ws = "default"
        mock_machinelearning_client.default_workspace_name = default_ws
        assert default_ws == mock_machinelearning_client.default_workspace_name


class TestWorkspaceOperation:
    @pytest.mark.parametrize('arg', ['resource_group', 'subscription', 'other_rand_str'])
    def test_list(self, arg: str, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.list(arg)
        if arg == 'subscription':
            mock_workspace_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_workspace_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.get(randstr)
        mock_workspace_operation._operation.get.assert_called_once()

    def test_create_or_update(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.create_or_update(randstr)
        mock_workspace_operation._operation.begin_create_or_update.assert_called_once()

    def test_delete(self, mock_workspace_operation: WorkspaceOperations, randstr: str) -> None:
        mock_workspace_operation.delete(randstr)
        mock_workspace_operation._operation.begin_delete.assert_called_once()


class TestJobOperations:
    def test_list(self, mock_job_operation: JobOperations) -> None:
        mock_job_operation.list()
        mock_job_operation._operation.list.assert_called_once()

    def test_get(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.get(randstr)
        mock_job_operation._operation.get.assert_called_once()

    def test_submit(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.submit(job_name=randstr, file="./tests/test_configs/command_job_test.yml")
        mock_job_operation._operation.create_or_update.assert_called_once()


class TestModelOperations:
    def test_create_file_mlflow_folder_not_set(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        with pytest.raises(Exception):
            mock_model_operation.create(randstr, version="15")

    def test_create_with_file(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation.create(randstr, file='./random_file')
        mock_model_operation._model_container_operation.create_or_update.assert_called_once()
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

    def test_show_name_and_version(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation.show(name=f"{randstr}:1")
        mock_model_operation._model_versions_operation.get.assert_called_once()
        assert mock_model_operation._model_container_operation.get.call_count == 0

    def test_show_only_name(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation._model_versions_operation.list.return_value = [Mock()]
        mock_model_operation.show(name=f"{randstr}")
        mock_model_operation._model_versions_operation.list.assert_called_once()
        assert "latest_version_only=True" in str(mock_model_operation._model_versions_operation.list.call_args)
        assert mock_model_operation._model_container_operation.get.call_count == 0

    def test_list(self, mock_model_operation: ModelOperations) -> None:
        mock_model_operation._model_container_operation.list.return_value = [Mock() for _ in range(5)]
        mock_model_operation._model_versions_operation.list.return_value = [Mock() for _ in range(5)]
        result = mock_model_operation.list(None)
        assert isinstance(result, list)
        mock_model_operation._model_container_operation.list.assert_called_once()
        r = list(result)
        assert mock_model_operation._model_versions_operation.list.call_count == 5
        assert len(r) == 5 * 5


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


class TestCodeOperations:
    def test_create(self, mock_code_operation: CodeOperations, randstr: str, artifact_path) -> None:
        with patch('azure.machinelearning._artifacts._artifact_utilities.upload_artifact',
                   return_value = (None, None)):
            mock_code_operation.create(name=randstr, directory=artifact_path)
        mock_code_operation._container_operation.create_or_update.assert_called_once()
        mock_code_operation._version_operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_code_operation._version_operation.create_or_update.call_args)

    def test_show(self, mock_code_operation: CodeOperations, randstr: str) -> None:
        mock_code_operation.show(name=f"{randstr}:1")
        mock_code_operation._version_operation.get.assert_called_once()
        assert mock_code_operation._version_operation.list.call_count == 0

    def test_show_only_name(self, mock_code_operation: CodeOperations, randstr: str) -> None:
        mock_code_operation._version_operation.list.return_value = [Mock()]
        mock_code_operation.show(name=f"{randstr}")
        mock_code_operation._version_operation.list.assert_called_once()
        assert "latest_version_only=True" in str(mock_code_operation._version_operation.list.call_args)
        assert mock_code_operation._container_operation.get.call_count == 0
    
    def test_get_job_logs(self, mock_job_operation: JobOperations, experiment_name: str, job_id: str) -> None:
        # TODO: full unit tests on this later
        pass

