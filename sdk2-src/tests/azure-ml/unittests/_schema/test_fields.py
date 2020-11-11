import pathlib
from pathlib import Path

import pytest
import yaml
from azure.ml._schema import InternalModel, ModelSchema, ArmVersionedStr, ArmStr
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow.exceptions import ValidationError
from marshmallow.schema import Schema
from marshmallow.fields import String


class DummySchema(Schema):
    environment = ArmStr()


class FooSchema(Schema):
    model = ArmVersionedStr()


class TestField:
    def test_arm_str(self) -> None:
        schema = DummySchema()
        input_data = {'environment': 'azureml:some_arm_id'}
        output_data = {'environment': 'some_arm_id'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == input_data

    def test_arm_str_failed(self) -> None:
        schema = DummySchema()
        input_data = {'environment': 'some_arm_id'}
        with pytest.raises(ValidationError):
            schema.load(input_data)

    def test_arm_versioned_str(self) -> None:
        schema = FooSchema()
        input_data = {'model': 'azureml:/subscription/something/other/value/name:some_version'}
        output_data = {'model': '/subscription/something/other/value/name/versions/some_version'}
        dumped_data = {'model': 'azureml:/subscription/something/other/value/name/versions/some_version'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        input_data = {'model': 'azureml:name:some_version'}
        output_data = {'model': 'name/versions/some_version'}
        dumped_data = {'model': 'azureml:name/versions/some_version'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

        input_data = {'model': 'azureml:name/versions/some_version'}
        output_data = {'model': 'name/versions/some_version'}
        dumped_data = {'model': 'azureml:name/versions/some_version'}
        data = schema.load(input_data)
        assert data == output_data
        assert schema.dump(data) == dumped_data

    def test_arm_versioned_str_failed(self) -> None:
        schema = FooSchema()
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
