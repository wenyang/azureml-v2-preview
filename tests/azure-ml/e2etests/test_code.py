import pytest
import uuid
from unittest.mock import patch

from azure.ml import MLClient
from utilities.utils import get_arm_id
from azure.ml._utils._asset_utils import _parse_name_version


@pytest.fixture
def uuid_name() -> str:
    name = str(uuid.uuid1()) + ":1"
    yield name


@pytest.fixture
def artifact_path(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name)


@pytest.fixture
def artifact_path_dir(tmpdir_factory) -> str:  # type: ignore
    file_name = tmpdir_factory.mktemp("artifact_testing_dir").join("artifact_file.txt")
    file_name.write('content')
    return str(file_name.dirpath()) + "\\"


@pytest.mark.e2etest
class TestCode:
    def test_create_and_show(self, client: MLClient, artifact_path: str, uuid_name: str) -> None:
        name, version = _parse_name_version(uuid_name)
        code_asset_1 = client.code.create(name=name, directory=artifact_path)
        code_asset_2 = client.code.show(name="{0}:{1}".format(name, version))

        arm_id = get_arm_id(
            ws_scope=client._workspace_scope,
            entity_name=name,
            entity_version=1,
            entity_type="codes"
        )

        assert code_asset_1.id == code_asset_2.id == arm_id

    def test_create_and_show_dir(self, client: MLClient, artifact_path_dir: str, uuid_name: str) -> None:
        name, version = _parse_name_version(uuid_name)
        code_asset_1 = client.code.create(name=name, directory=artifact_path_dir)
        code_asset_2 = client.code.show(name="{0}:{1}".format(name, version))

        arm_id = get_arm_id(
            ws_scope=client._workspace_scope,
            entity_name=name,
            entity_version=1,
            entity_type="codes"
        )

        assert code_asset_1.id == code_asset_2.id == arm_id

    def test_create_and_show_current_dir(self, client: MLClient, uuid_name: str) -> None:
        name, version = _parse_name_version(uuid_name)
        code_asset_1 = client.code.create(name=name, directory=".")
        code_asset_2 = client.code.show(name="{0}:{1}".format(name, version))

        arm_id = get_arm_id(
            ws_scope=client._workspace_scope,
            entity_name=name,
            entity_version=1,
            entity_type="codes"
        )

        assert code_asset_1.id == code_asset_2.id == arm_id

    def test_asset_path_update(self, client: MLClient, uuid_name: str, artifact_path: str) -> None:
        name, version = _parse_name_version(uuid_name)
        client.code.create(name=name, directory=artifact_path)

        # create same name and version code asset again with different content hash/asset paths
        with pytest.raises(Exception):
            with patch('azure.ml._artifacts._artifact_utilities.get_object_hash', return_value=uuid.uuid4()):
                client.code.create(name=name, directory=artifact_path)
