from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from azure.ml._operations import DatastoreOperations, ModelOperations
from azure.ml._workspace_dependent_operations import WorkspaceScope


@pytest.fixture
def mock_datastore_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock) -> DatastoreOperations:
    yield DatastoreOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services)


@pytest.fixture
def mock_model_operation(mock_workspace_scope: WorkspaceScope, mock_aml_services: Mock, mock_datastore_operation: Mock) -> ModelOperations:
    yield ModelOperations(workspace_scope=mock_workspace_scope, service_client=mock_aml_services, datastore_operations=mock_datastore_operation)


class TestModelOperations:
    def test_create_name_not_set(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        with pytest.raises(Exception):
            mock_model_operation.create(path=randstr, version=15)

    # @patch('azure.ml._artifacts._artifact_utilities.StorageClient', Mock())
    # def test_create_with_name_path(self, mock_model_operation: ModelOperations, randstr: str, tmp_path: Path) -> None:
    #     model_path = tmp_path / "model.pkl"
    #     model_path.write_text('hello world')
    #     mock_model_operation.create(path=model_path, name=randstr, version=1)
    #     mock_model_operation._model_container_operation.create_or_update.assert_called_once()
    #     mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
    #     assert "version=1" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

    def test_create_with_spec_file(self, mock_model_operation: ModelOperations, randstr: str, tmp_path: Path) -> None:
        p = tmp_path / "model_full.yml"
        model_path = tmp_path / 'model.pkl'
        model_path.write_text('hello world')
        p.write_text(f"""
name: model_{randstr}
asset_path: ./model.pkl
version: 3""")
        with patch('azure.ml._operations.model_operations._upload_to_datastore', return_value=(None, None)):
            mock_model_operation.create(file=p)
        mock_model_operation._model_container_operation.create_or_update.assert_called_once()
        mock_model_operation._model_versions_operation.create_or_update.assert_called_once()
        assert "version=3" in str(mock_model_operation._model_versions_operation.create_or_update.call_args)

    def test_show_name_and_version(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation.show(name=randstr, version=1)
        mock_model_operation._model_versions_operation.get.assert_called_once()
        assert mock_model_operation._model_container_operation.get.call_count == 0

    def test_list(self, mock_model_operation: ModelOperations, randstr: str) -> None:
        mock_model_operation._model_container_operation.list.return_value = [Mock() for _ in range(5)]
        mock_model_operation._model_versions_operation.list.return_value = [Mock() for _ in range(5)]
        result = mock_model_operation.list()
        assert isinstance(result, list)
        mock_model_operation._model_container_operation.list.assert_called_once()
        result = mock_model_operation.list(randstr)
        mock_model_operation._model_versions_operation.list.assert_called_once()
