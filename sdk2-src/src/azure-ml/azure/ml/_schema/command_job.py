# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from typing import Dict, Optional
from .base import PatchedNested
from .compute_binding import ComputeBindingSchema
from .resource import ResourceSchema
from .environment import InternalEnvironment
from .job_metadata import JobMetadataSchema, InternalJobMetadata
from .command_component import InternalCommandComponent, CommandComponentSchema
from .._restclient.machinelearningservices.models import CommandJobResource, CommandJob, \
    ComputeBinding, CodeConfiguration


# The reason for having a class representation matching the yaml
# structure is to support cli args that set properties matching the
# yaml paths. Having getters and setters for nested objects to ensure
# instantiated correctly and then validate before sending.
class InternalCommandJob:
    def __init__(
        self,
        *,
        metadata: Optional[InternalJobMetadata] = None,
        name: str = None,
        run: InternalCommandComponent = None,
        on_compute: ComputeBinding = None,
        max_run_duration_seconds: Optional[int] = None,
        data_bindings: Optional[Dict[str, "DataBinding"]] = None,
        distribution_configuration: Optional["DistributionConfiguration"] = None,
        experiment_name: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self._name = name
        self.metadata = metadata
        self._run = run
        self._on_compute = on_compute
        self.experiment_name = experiment_name
        self.properties = properties
        self.status = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def run(self) -> InternalCommandComponent:
        return self._run

    @property
    def on_compute(self) -> ComputeBinding:
        return self._on_compute

    @on_compute.setter
    def on_compute(self, value: ComputeBinding) -> None:
        self._on_compute = value

    def validate(self):
        if self.name is None:
            raise NameError("name is required")
        if self.on_compute is None:
            raise NameError("on_compute is required")
        if self.run is None:
            raise NameError("run is required")
        if self.run.command is None:
            raise NameError("run.command is required")
        if self.run.environment is None:
            raise NameError("run.environment is required for non-local runs")

    def translate_to_rest_object(self) -> CommandJobResource:
        self.validate()
        # TODO: build out data bindings and replace in command
        data_bindings = {}
        properties = CommandJob(
            code_configuration=CodeConfiguration(command=self._run.command.split()),
            compute_binding=self.on_compute,
            properties=self.properties,
            experiment_name=self.experiment_name,
            data_bindings=data_bindings,
            environment_id=self._run.environment.name
        )
        result = CommandJobResource(properties=properties)
        result.name = self.name
        return result

    def serialize_from_rest_object(self, obj: CommandJobResource):
        properties = obj.properties
        # seeing issue where deserialization from the autorest function isn't deserializing recursive
        if type(properties) is not CommandJob:
            properties["code_configuration"] = CodeConfiguration(**properties["codeConfiguration"])
            properties["compute_binding"] = ComputeBinding(**properties["computeBinding"])
            properties = CommandJob(properties=properties)
        self._on_compute = properties.compute_binding
        self.name = obj.name
        self.properties = properties.properties
        self.experiment_name = properties.experiment_name
        self._run = InternalCommandComponent(
            command=" ".join(properties.code_configuration.command),
            environment=InternalEnvironment(name=properties.environment_id))
        self.metadata = InternalJobMetadata(
            startTimeUtc=obj.system_data.created_at,
            interaction_endpoints=properties.interaction_endpoints)
        self.status = properties.status
        return CommandJobSchema().dump(self)    # type: ignore


class CommandJobSchema(ResourceSchema):
    metadata = PatchedNested(JobMetadataSchema, dump_only=True)
    run = PatchedNested(CommandComponentSchema)
    name = fields.Str()
    # on is a reserved word in yaml, we can escape it in quotes or use a different key.
    # I've opted for on_compute as a working substitution
    on_compute = PatchedNested(ComputeBindingSchema)
    inputs = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())
    outputs = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())
    status = fields.Str(dump_only=True)
    environment_id = fields.Str()
    experiment_name = fields.Str()
    job_type = fields.Str()
    properties = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        return InternalCommandJob(**data)
