# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ml._schema.full_schema import InternalFullSchemaObject
from azure.ml._schema.code_configuration_schema import InternalCodeConfiguration
from azure.ml._schema.environment import InternalEnvironment
from azure.ml._schema.model import InternalModel
from azure.ml._utils._arm_id_utils import parse_name_version
from azure.ml._workspace_dependent_operations import OperationsContainer


class OperationOrchestrator(object):
    def __init__(self, operation_container: OperationsContainer):
        self._operation_container = operation_container

    def get_code_asset_arm_id(self, code_configuration: InternalFullSchemaObject[InternalCodeConfiguration]) -> str:
        if code_configuration.arm_id:
            return code_configuration.arm_id
        _code_assets = self._operation_container.all_operations["code_assets"]
        if code_configuration.name:
            return _code_assets.show(name=code_configuration.name).id
        elif code_configuration.settings:
            return _code_assets._get_code_artifact_arm_id(code=code_configuration.settings.code)

    def get_environment_arm_id(self, environment: InternalFullSchemaObject[InternalEnvironment]) -> str:
        if environment.arm_id:
            return environment.arm_id
        _environments = self._operation_container.all_operations["environments"]
        if environment.name:
            name, version = parse_name_version(name=environment.name)
            if not version:
                version = "latest"
            return _environments.get(environment_name=name, environment_version=version).id
        elif environment.settings:
            return _environments._create_or_update(environment=environment.settings).id

    def get_model_arm_id(self, model: InternalFullSchemaObject[InternalModel]):
        if model.arm_id:
            return model.arm_id
        _model = self._operation_container.all_operations["model"]
        if model.name:
            return _model.show(name=model.name).id
        elif model.settings:
            return _model._create_model(internal_model=model.settings).id
