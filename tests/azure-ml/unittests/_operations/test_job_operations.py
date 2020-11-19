import pytest
from mock import patch
from unittest.mock import Mock
from azure.ml._operations import JobOperations, WorkspaceOperations, CodeOperations, DatastoreOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_code_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock) -> CodeOperations:
    yield CodeOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, datastore_operations=mock_datastore_operation)


@pytest.fixture
def mock_workspace_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> WorkspaceOperations:
    yield WorkspaceOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_job_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_code_operation: Mock, mock_workspace_operations: WorkspaceOperations) -> JobOperations:
    yield JobOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, code_operations=mock_code_operation, workspace_ops=mock_workspace_operations)


class TestJobOperations:
    def test_list(self, mock_job_operation: JobOperations) -> None:
        mock_job_operation.list()
        mock_job_operation._operation.list.assert_called_once()

    def test_get(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.get(randstr)
        mock_job_operation._operation.get.assert_called_once()

    def test_submit_command_job(self, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_job_operation.submit(job_name=randstr, file="./tests/test_configs/command_job_test.yml")
        mock_job_operation._operation.create_or_update.assert_called_once()

    '''
    @patch('azure.ml._operations.job_operations.JobLogManager')
    @patch('azure.ml._operations.JobOperations._get_workspace_url')
    def test_get_job_logs(self, mock_workspace_url, mock_job_log_manager, mock_job_operation: JobOperations, randstr: str) -> None:
        mock_workspace_url.return_value = "https://test.com"
        mock_log_manager_return = Mock()
        mock_log_manager_return.download_all_job_logs.return_value = ["test"]
        mock_job_log_manager.return_value = mock_log_manager_return
        mock_job_operation.download_job_logs(exp_name=randstr, job_name=randstr)
        mock_workspace_url.assert_called_once()
        mock_log_manager_return.download_all_job_logs.assert_called_once()
    '''

