from azure.ml._schema import ModelSchema, InternalModel
# from azure.ml._restclient.machinelearningservices.models import CommandJobResource

import yaml
import pytest


class TestModelSchema:
    def test_deserialize(self) -> None:
        with open("./tests/test_configs/model_full.yml", 'r') as f:
            target = yaml.safe_load(f)
            internal_model: InternalModel = ModelSchema().load(target)
            assert internal_model.asset_path == './model.pkl'
