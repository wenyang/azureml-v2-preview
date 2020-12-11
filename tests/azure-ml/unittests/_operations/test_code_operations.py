import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._operations import CodeOperations, DatastoreOperations
import uuid


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write("content")
    return str(file_name)


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_code_operation(
    mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock
) -> CodeOperations:
    yield CodeOperations(
        workspace_scope=mock_workspace_scope,
        service_client=mock_aml_services,
        datastore_operations=mock_datastore_operation,
    )


@pytest.fixture
def uuid_name() -> str:
    yield str(uuid.uuid1())


class TestCodeOperations:
    def test_create(self, mock_code_operation: CodeOperations, uuid_name: str, artifact_path: str) -> None:
        with patch("azure.ml._operations.code_operations._upload_to_datastore", return_value=(None, None)):
            mock_code_operation.create(name=uuid_name, directory=artifact_path)
        mock_code_operation._version_operation.create_or_update.assert_called_once()
        assert "version=1" in str(mock_code_operation._version_operation.create_or_update.call_args)

    def test_show(self, mock_code_operation: CodeOperations, randstr: str) -> None:
        mock_code_operation.show(name=f"{randstr}:1")
        mock_code_operation._version_operation.get.assert_called_once()
        assert mock_code_operation._version_operation.list.call_count == 0

    def test_name_not_guid(self, mock_code_operation: CodeOperations, artifact_path: str) -> None:
        with pytest.raises(Exception):
            mock_code_operation.create(name="not a guid", directory=artifact_path)

    def test_version_not_int(self, mock_code_operation: CodeOperations, uuid_name: str, artifact_path: str) -> None:
        with pytest.raises(Exception):
            mock_code_operation.create(name=uuid_name, version="1.0", directory=artifact_path)
