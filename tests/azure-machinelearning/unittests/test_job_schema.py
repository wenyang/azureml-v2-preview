from azure.machinelearning._schema import CommandJobSchema, InternalCommandJob
from azure.machinelearning._restclient.machinelearningservices.models import CommandJobResource

import yaml
import pytest

class TestCommandJob:
    def test_deserialize(self):
        with open("./tests/test_configs/command_job_rest.yml", 'r') as f:
            target = yaml.safe_load(f)
        with open("./tests/test_configs/command_job_test.yml", 'r') as f:
            cfg = yaml.safe_load(f)
            internal_representation: InternalCommandJob = CommandJobSchema().load(cfg)
        source = internal_representation.translate_to_rest_object()
        assert source.name == target["name"]
        assert source.properties.code_configuration.command == target["properties"]["codeConfiguration"]["command"]
