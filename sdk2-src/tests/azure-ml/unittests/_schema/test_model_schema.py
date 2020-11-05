import pathlib
from pathlib import Path

import pytest
import yaml
from azure.ml._schema import InternalModel, ModelSchema
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from marshmallow.exceptions import ValidationError


class TestModelSchema:
    def test_deserialize(self) -> None:
        path = Path("./tests/test_configs/model_full.yml")
        with open(path, 'r') as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            schema = ModelSchema(context=context)
            internal_model = schema.load(target)
            assert internal_model.asset_path == './model.pkl'

    def test_deserialize_env_with_only_name(self) -> None:
        path = Path("./tests/test_configs/model_env2.yml")
        with open(path, 'r') as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            schema = ModelSchema(context=context)
            internal_model = schema.load(target)
            assert internal_model.environment == '/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/Environments/AzureML-Minimal'
        path = Path("./tests/test_configs/model_env1.yml")
        with open(path, 'r') as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            schema = ModelSchema(context=context)
            internal_model = schema.load(target)
            assert internal_model.environment == 'Environments/AzureML-Minimal'

    def test_desrialize_env_with_bad_prefix(self) -> None:
        path = Path("./tests/test_configs/model_bad.yml")
        with open(path, 'r') as f:
            target = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: path.parent}
            schema = ModelSchema(context=context)
            with pytest.raises(ValidationError):
                schema.load(target)
