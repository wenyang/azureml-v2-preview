# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from typing import Dict, Optional, Union
from azure.ml.constants import BASE_PATH_CONTEXT_KEY
from .schema import PatchedNested, PathAwareSchema
from .fields import ArmVersionedStr, ArmStr
import re
from .input_entry import InputEntrySchema
from .input_port import InputPort
from .compute_binding import ComputeBindingSchema
from .code_asset import CodeAssetSchema
from .union_field import UnionField
from .job_metadata import JobMetadataSchema, InternalJobMetadata
from .._restclient.machinelearningservices.models import DataBinding
from .._restclient.machinelearningservices.models import CommandJobResource, CommandJob, \
    ComputeBinding, CodeConfiguration


# The reason for having a class representation matching the yaml
# structure is to support cli args that set properties matching the
# yaml paths. Having getters and setters for nested objects to ensure
# instantiated correctly and then validate before sending.
class InternalCommandJob:
    INPUT_BINDING_PREFIX = "AZURE_ML_INPUT"

    def __init__(
        self,
        base_path: Optional[str] = None,
        *,
        metadata: Optional[InternalJobMetadata] = None,
        name: str = None,
        compute: ComputeBinding = None,
        max_run_duration_seconds: Optional[int] = None,
        data_bindings: Optional[Dict[str, "DataBinding"]] = None,
        distribution_configuration: Optional["DistributionConfiguration"] = None,
        experiment_name: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        inputs: Optional[Dict[str, "InputEntry"]] = {},
        command: str,
        code: Union["InternalCodeAsset", str, None] = None,
        environment: Optional[str] = None,
        input_ports: Optional[Dict[str, "InputPort"]] = {},
        **kwargs
    ):
        self._name = name
        self.metadata = metadata
        self._compute = compute
        self.experiment_name = experiment_name
        self.properties = properties
        self.status = None
        self.input_values = inputs
        self._command = command
        self._environment = environment
        self._input_ports = input_ports
        self._bound_command = None
        self._data_bindings = None
        self._base_path = base_path
        # Anticipate the union type of asset/arm_id
        if isinstance(code, str):
            self._code_arm_id = code
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
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def compute(self) -> ComputeBinding:
        return self._compute

    @compute.setter
    def compute(self, value: ComputeBinding) -> None:
        self._compute = value

    def add_implicit_ports(self):
        implicit_inputs = re.findall(r'\{inputs\.([\w\.-]+)}', self._command)
        for key in implicit_inputs:
            if not self._input_ports.get(key, None):
                self._input_ports[key] = InputPort(type_string="null", optional=False)

    def bind_inputs(self) -> Dict[str, "DataBinding"]:
        self.add_implicit_ports()
        data_bindings = {}

        self._bound_command = self._command
        input_index = 0
        for key, port in self._input_ports.items():
            connected_value = self.input_values.get(key, None)
            value = connected_value.name or port.default
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

    def upload_dependencies(self, code_operations: "CodeOperations"):
        # TODO: this will need to be paralelized when multiple tasks
        # are required. Also consider the implications for dependencies.
        if self._code_asset is not None:
            self._code_arm_id = self._code_asset.check_or_create_code_asset(code_operations)

    def validate(self):
        if self.name is None:
            raise NameError("name is required")
        if self.compute is None:
            raise NameError("compute is required")
        if self._bound_command is None:
            raise NameError("run.command is required")
        if self.environment is None:
            raise NameError("run.environment is required for non-local runs")

    def generate_code_configuration(self) -> CodeConfiguration:
        return CodeConfiguration(command=self._bound_command.split(), code_artifact_id=self._code_arm_id)

    def translate_to_rest_object(self) -> CommandJobResource:
        self.bind_inputs()
        self.validate()
        # TODO: build out data bindings and replace in command
        properties = CommandJob(
            code_configuration=self.generate_code_configuration(),
            compute_binding=self.compute,
            properties=self.properties,
            experiment_name=self.experiment_name,
            data_bindings=self._data_bindings,
            environment_id=self.environment
        )
        result = CommandJobResource(properties=properties)
        result.name = self.name
        return result

    def serialize_from_rest_object(self, obj: CommandJobResource):
        properties = obj.properties
        # seeing issue where deserialization from the autorest function isn't deserializing recursive
        if type(properties) is not CommandJob:
            code_configuration = CodeConfiguration(**properties["codeConfiguration"])
            compute_binding = ComputeBinding(**properties["computeBinding"])
            properties = CommandJob(properties=properties, compute_binding=compute_binding, code_configuration=code_configuration)
        self._on_compute = properties.compute_binding
        self.name = obj.name
        self.properties = properties.properties
        self.experiment_name = properties.experiment_name
        self.command = " ".join(properties.code_configuration.command)
        self.environment = properties.environment_id
        self.metadata = InternalJobMetadata(
            startTimeUtc=obj.system_data.created_at,
            interaction_endpoints=properties.interaction_endpoints)
        self.status = properties.status
        return CommandJobSchema().dump(self)    # type: ignore


class CommandJobSchema(PathAwareSchema):
    metadata = PatchedNested(JobMetadataSchema, dump_only=True)
    name = fields.Str()
    command = fields.Str()
    # TODO: make union type of nested asset or armString when Union is available
    code = UnionField([PatchedNested(CodeAssetSchema), ArmVersionedStr()])
    environment = ArmStr()
    compute = PatchedNested(ComputeBindingSchema)
    inputs = fields.Dict(
        keys=fields.Str(),
        values=PatchedNested(InputEntrySchema))
    outputs = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())
    status = fields.Str(dump_only=True)
    experiment_name = fields.Str()
    job_type = fields.Str()
    properties = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        return InternalCommandJob(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
