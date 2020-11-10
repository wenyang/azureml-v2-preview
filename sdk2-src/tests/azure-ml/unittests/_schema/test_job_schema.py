from azure.ml._schema import CommandJobSchema, InternalCommandJob
from azure.ml._restclient.machinelearningservices.models import CommandJobResource
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from pathlib import Path
import yaml
import pytest


class TestCommandJob:
    def test_deserialize(self):
        test_path = "./tests/test_configs/command_job_test.yml"
        with open("./tests/test_configs/command_job_rest.yml", 'r') as f:
            target = yaml.safe_load(f)
        with open(test_path, 'r') as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            schema = CommandJobSchema(context=context)
            internal_representation: InternalCommandJob = schema.load(cfg)
        source = internal_representation.translate_to_rest_object()
        assert source.name == target["name"]
        assert source.properties.code_configuration.command == target["properties"]["codeConfiguration"]["command"]
