from azure.ml._schema import CommandJobSchema, InternalCommandJob
from azure.ml._workspace_dependent_operations import WorkspaceScope
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, WORKSPACE_CONTEXT_KEY
from pathlib import Path
from marshmallow.exceptions import ValidationError
import yaml
import pytest


class TestCommandJob:
    def test_deserialize(self, mock_workspace_scope: WorkspaceScope):
        test_path = "./tests/test_configs/jobs/command_job_test.yml"
        with open("./tests/test_configs/jobs/command_job_rest.yml", "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            context[WORKSPACE_CONTEXT_KEY] = mock_workspace_scope
            schema = CommandJobSchema(context=context)
            internal_representation: InternalCommandJob = schema.load(cfg)
        source = internal_representation.translate_to_rest_object()
        assert source.name == target["name"]
        assert source.properties.code_configuration.command == target["properties"]["codeConfiguration"]["command"]

    @pytest.fixture(
        params=[
            "./tests/test_configs/jobs/dist_job_1.yml",
            "./tests/test_configs/jobs/dist_job_1.yml",
            "./tests/test_configs/jobs/dist_job_1.yml",
        ]
    )
    def test_distributions_roundtrip(self, mock_workspace_scope: WorkspaceScope, request):
        context = {BASE_PATH_CONTEXT_KEY: Path(request.param).parent}
        context[WORKSPACE_CONTEXT_KEY] = mock_workspace_scope
        schema = CommandJobSchema(context=context)
        cfg = None
        for path in request.param:
            with open(path, "r") as f:
                cfg = yaml.safe_load(f)
            internal_representation: InternalCommandJob = schema.load(cfg)
            rest_intermediate = internal_representation.translate_to_rest_object()
            internal_obj = InternalCommandJob()
            internal_obj.load(rest_intermediate)
            reconstructed_yaml = schema.dump(internal_obj)
            assert reconstructed_yaml["distribution"] == cfg["distribution"]

    def test_invalid_distribution_config(self, mock_workspace_scope: WorkspaceScope):
        path = "./tests/test_configs/jobs/dist_job_bad.yml"
        context = {BASE_PATH_CONTEXT_KEY: Path(path).parent}
        context[WORKSPACE_CONTEXT_KEY] = mock_workspace_scope
        schema = CommandJobSchema(context=context)
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
            with pytest.raises(ValidationError):
                schema.load(cfg)

    def test_deserialize_inputs(self, mock_workspace_scope: WorkspaceScope):
        test_path = "./tests/test_configs/jobs/command_job_inputs_test.yml"
        with open("./tests/test_configs/jobs/command_job_inputs_rest.yml", "r") as f:
            target = yaml.safe_load(f)
        with open(test_path, "r") as f:
            cfg = yaml.safe_load(f)
            context = {BASE_PATH_CONTEXT_KEY: Path(test_path).parent}
            context[WORKSPACE_CONTEXT_KEY] = mock_workspace_scope
            schema = CommandJobSchema(context=context)
            internal_representation: InternalCommandJob = schema.load(cfg)
        source = internal_representation.translate_to_rest_object()
        assert (
            source.properties.data_bindings["test1"].source_data_reference
            == target["properties"]["dataBindings"]["test1"]["sourceDataReference"]
        )
