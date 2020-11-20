# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Dict, Optional, Union, Any
from marshmallow import fields, post_load
from azure.ml.constants import AssetType, BASE_PATH_CONTEXT_KEY
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration, \
    DataBinding, ComputeBinding
from ..schema import PatchedNested, PathAwareSchema
from ..fields import ArmVersionedStr
from ..union_field import UnionField
from .input_entry import InputEntry, InputEntrySchema
from .input_port import InputPort
from ..code_asset import CodeAssetSchema
from ..compute_binding import ComputeBindingSchema
from .loadable_mixin import LoadableMixin


class ParameterizedCommand(LoadableMixin):
    INPUT_BINDING_PREFIX = "AZURE_ML_INPUT"

    def __init__(
        self,
        base_path: Optional[str] = None,
        data_bindings: Optional[Dict[str, "DataBinding"]] = None,
        inputs: Optional[Dict[str, "InputEntry"]] = None,
        command: str = "",
        compute: ComputeBinding = None,
        code: Union["InternalCodeAsset", str, None] = None,
        environment: Optional[str] = None,
        input_ports: Optional[Dict[str, "InputPort"]] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.input_values = inputs or {}
        self._command = command
        self._environment = environment
        self._input_ports = input_ports or {}
        self._bound_command: str
        self._data_bindings: Dict[str, Any] = {}
        self._base_path = base_path
        self.compute = compute
        # Anticipate the union type of asset/arm_id
        if isinstance(code, str):
            self._code_arm_id: Optional[str] = code
            self._code_asset = None
        else:
            self._code_asset = code
            self._code_arm_id = None

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, value: str) -> None:
        self._command = value

    @property
    def environment(self) -> Optional[str]:
        return self._environment

    @environment.setter
    def environment(self, value: str) -> None:
        self._environment = value

    @property
    def code(self) -> Optional[str]:
        return self._code_arm_id

    def add_implicit_ports(self) -> None:
        implicit_inputs = re.findall(r'\{inputs\.([\w\.-]+)}', self._command)
        for key in implicit_inputs:
            if not self._input_ports.get(key, None):
                self._input_ports[key] = InputPort(type_string="null", optional=False)

    def bind_inputs(self) -> None:
        self.add_implicit_ports()
        data_bindings: Dict[str, Any] = {}

        self._bound_command = self._command
        input_index = 0
        for key, port in self._input_ports.items():
            connected_value = self.input_values.get(key, None)
            value = connected_value.data or port.default
            if not value and not port.optional:
                raise Exception("Missing required input: " + key)
            # handle constants directly
            if port.type_string == "number" or (port.type_string == "null" and connected_value.mode is None):
                self._bound_command = re.sub(r'\{inputs\.' + key + '}', value, self._bound_command)
            else:
                local_reference = self.INPUT_BINDING_PREFIX + str(input_index)
                data_bindings[key] = DataBinding(
                    source_data_reference=value,
                    local_reference=local_reference,
                    mode=connected_value.mode
                )
                self._bound_command = re.sub(r'\{inputs\.' + key + '}', local_reference, self._bound_command)
                input_index += 1
        self._data_bindings = data_bindings

    def unbind_inputs(self, properties: Any) -> None:
        # TODO: Remove when MFE no longer requires tokenized command
        command = properties.code_configuration.command
        inputs = {}

        for key, input in properties.data_bindings.items():
            command = re.sub(input.local_reference, "{inputs." + key + "}", command)
            inputs[key] = InputEntry(mode=input.mode, data=input.source_data_reference)
        self.inputs = inputs
        self.command = command

    def upload_dependencies(self, code_operations: "CodeOperations") -> None:
        # TODO: this will need to be paralelized when multiple tasks
        # are required. Also consider the implications for dependencies.
        if self._code_asset is not None:
            self._code_arm_id = self._code_asset.check_or_create_code_asset(code_operations)

    def generate_code_configuration(self) -> CodeConfiguration:
        return CodeConfiguration(command=self._bound_command, code_artifact_id=self._code_arm_id)

    def load(self, obj: Any) -> None:
        super().load(obj)
        self.unbind_inputs(obj)
        self._code_arm_id = obj.code_configuration.code_artifact_id
        if hasattr(obj, "compute_binding"):
            self.compute = obj.compute_binding
        self._environment = obj.environment_id


class ParameterizedCommandSchema(PathAwareSchema):
    command = fields.Str()
    code = UnionField([PatchedNested(CodeAssetSchema), ArmVersionedStr(asset_type=AssetType.CODE)])
    environment = ArmVersionedStr(asset_type=AssetType.ENVIRONMENT)
    compute = PatchedNested(ComputeBindingSchema)
    inputs = fields.Dict(
        metadata={
            "values": PatchedNested(InputEntrySchema)
        },
        keys=fields.Str(),
        values=PatchedNested(InputEntrySchema))


class TrialJobSchema(ParameterizedCommandSchema):
    @post_load
    def make(self, data: Any, **kwargs: Any) -> ParameterizedCommand:
        return ParameterizedCommand(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
