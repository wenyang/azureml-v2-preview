# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union
from azure.ml._schema.code_configuration_schema import InternalCodeConfiguration
from azure.ml._schema.environment import InternalEnvironment
from azure.ml._schema.model import InternalModel
from azure.ml._utils._arm_id_utils import parse_name_version
from azure.ml._schema.code_asset import InternalCodeAsset
from azure.ml._workspace_dependent_operations import OperationsContainer
from azure.ml._utils._arm_id_utils import is_arm_id


class OperationOrchestrator(object):
    def __init__(self, operation_container: OperationsContainer):
        self._operation_container = operation_container

    def get_code_asset_arm_id(self, code_configuration: InternalCodeConfiguration) -> str:
        _code_assets = self._operation_container.all_operations["code"]
        if is_arm_id(code_configuration.code):
            return code_configuration.code
        elif isinstance(code_configuration.code, str):
            return _code_assets.show(name=code_configuration).id
        elif isinstance(code_configuration.code, InternalCodeAsset):
            return code_configuration.code.check_or_create_code_asset(_code_assets)

    def get_environment_arm_id(self, environment: Union[str, InternalEnvironment]) -> str:
        if is_arm_id(environment):
            return environment
        _environments = self._operation_container.all_operations["environments"]
        if isinstance(environment, str):
            name, version = parse_name_version(environment)
            if version:
                return _environments.get(environment_name=name,
                                         environment_version=version).id
            return _environments.get_latest_version(environment)
        elif isinstance(environment, InternalEnvironment):
            return _environments._create_or_update(environment=environment).id

    def get_model_arm_id(self, model: Union[str, InternalModel]):
        if is_arm_id(model):
            return model
        _model = self._operation_container.all_operations["model"]
        if isinstance(model, str):
            return _model.show(name=model)
        elif isinstance(model, InternalModel):
            return _model._create_model(internal_model=model).id
