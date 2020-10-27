import pytest
from pytest_mock import MockFixture
from unittest.mock import Mock, patch
from pathlib import Path
from azure.ml._operations import ModelOperations, DatastoreOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._artifacts._storage_helper import StorageClient


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_model_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock) -> ModelOperations:
    yield ModelOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, datastore_operations=mock_datastore_operation)


class TestModelOperations:
    def test_create_file_mlflow_folder_not_set(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        with pytest.raises(Exception):
            mock_model_operation.create(randstr, version="15")

    @patch('azure.ml._artifacts._artifact_utilities.StorageClient', Mock())
    def test_create_with_name_path(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation.create(path='tests/test_configs/model.pkl', name=f"{randstr}:1")
        mock_model_operation._model_container_operation.create_or_update.assert_called_once()
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
        assert "version='1'" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

    @patch('azure.ml._operations.model_operations.Path', Mock())
    @patch('azure.ml._artifacts._artifact_utilities.StorageClient', Mock())
    def test_create_with_spec_file(self, mock_model_operation: ModelOperations, randstr: str, tmp_path: Path) -> None:
        p = tmp_path / "full_spec.yml"
        p.write_text("""
name: test_model
asset_path: ./random/path/model.pkl
version: 3""")  # TODO: is version a int or string? Confused.
        mock_model_operation.create(file=p)
        mock_model_operation._model_container_operation.create_or_update.assert_called_once()
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
        assert "version=3" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

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
