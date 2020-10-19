import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from azure.machinelearning._workspace_dependent_operations import WorkspaceScope
from azure.machinelearning._operations import CodeOperations


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)


@pytest.fixture
def mock_code_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> CodeOperations:
    yield CodeOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


class TestCodeOperations():
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
