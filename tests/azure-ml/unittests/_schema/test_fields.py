import pathlib
from pathlib import Path

import pytest
import yaml
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml._schema import InternalModel, ModelSchema, ArmVersionedStr, ArmStr
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, AZUREML_RESOURCE_PROVIDER, RESOURCE_ID_FORMAT, WORKSPACE_CONTEXT_KEY
from marshmallow.exceptions import ValidationError
from marshmallow.schema import Schema
from marshmallow.fields import String


class DummyStr(ArmStr):
    def __init__(self, **kwargs):
        super().__init__()
        self.asset_type = "dummy"


class FooVersionedStr(ArmVersionedStr):
    def __init__(self, **kwargs):
        super().__init__()
        self.asset_type = "foo"

class DummySchema(Schema):
    environment = DummyStr()


class FooSchema(Schema):
    model = FooVersionedStr()


class TestField:
    def test_arm_str(self, mock_workspace_scope: WorkspaceScope) -> None:
        schema = DummySchema(context={WORKSPACE_CONTEXT_KEY: mock_workspace_scope})
        name = "resourceName"
        resource_id = RESOURCE_ID_FORMAT.format(
                                                mock_workspace_scope.subscription_id,
                                                mock_workspace_scope.resource_group_name,
                                                AZUREML_RESOURCE_PROVIDER,
                                                mock_workspace_scope.workspace_name) + \
                f"/dummy/{name}"
        input_data = {'environment': f'azureml:{name}'}
        output_data = {'environment': resource_id}
        dumped_data = {'environment': f'azureml:{resource_id}'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_str_failed(self) -> None:
        schema = DummySchema()
        input_data = {'environment': 'some_arm_id'}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_arm_versioned_str(self, mock_workspace_scope: WorkspaceScope) -> None:
        name = "resourceName"
        version = "3.14"
        resource_id_without_version = RESOURCE_ID_FORMAT.format(
                                                                mock_workspace_scope.subscription_id,
                                                                mock_workspace_scope.resource_group_name,
                                                                AZUREML_RESOURCE_PROVIDER,
                                                                mock_workspace_scope.workspace_name) + \
            f"/foo/{name}"
        resource_id = f"{resource_id_without_version}/versions/{version}"
        schema = FooSchema(context={WORKSPACE_CONTEXT_KEY: mock_workspace_scope})
        input_data = {'model': f'azureml:{name}:{version}'}
        output_data = {'model': resource_id}
        dumped_data = {'model': f'azureml:{resource_id}'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        input_data = {'model': f'azureml:{resource_id_without_version}:{version}'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        input_data = {'model': f'azureml:{name}/versions/{version}'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_versioned_str_failed(self, mock_workspace_scope: WorkspaceScope) -> None:
        schema = FooSchema(context={WORKSPACE_CONTEXT_KEY: mock_workspace_scope})
        input_data = {'model': '/subscription/something/other/value/name:some_version'}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {'model': 'azureml:/subscription/something/other/value/name'}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {'model': 'azureml:/subscription/something/other/value/name/versions'}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {'model': 'azureml:/subscription/something/other/value/name/versions/'}
        with pytest.raises(ValidationError):
            schema.load(input_data)
        input_data = {'model': 'azureml:/subscription/something/other/value/name/'}
