import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock
from azure.machinelearning._operations import JobOperations
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_job_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> JobOperations:
    yield JobOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


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