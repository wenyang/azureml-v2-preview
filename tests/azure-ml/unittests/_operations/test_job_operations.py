import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.ml._operations import JobOperations, WorkspaceOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_workspace_operations(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> WorkspaceOperations:
    yield WorkspaceOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_job_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_workspace_operations: WorkspaceOperations) -> JobOperations:
    yield JobOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, workspace_ops=mock_workspace_operations)


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

    def test_get_job_logs(self, mock_job_operation: JobOperations, randstr: str) -> None:
        ''' # TODO
        mock_job_operation.get_job_logs(exp_name=randstr, job_name=randstr)
        mock_job_operation.get_job_logs.assert_called_once()
        '''
