# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from typing import Optional
from azure.ml.constants import BASE_PATH_CONTEXT_KEY

from azure.ml._restclient.machinelearningservices.models import CommandJobResource, CommandJob
from .parameterized_command import ParameterizedCommand, ParameterizedCommandSchema
from .base_job import BaseJob, BaseJobSchema


# The reason for having a class representation matching the yaml
# structure is to support cli args that set properties matching the
# yaml paths. Having getters and setters for nested objects to ensure
# instantiated correctly and then validate before sending.
class InternalCommandJob(BaseJob, ParameterizedCommand):
    def __init__(
        self,
        max_run_duration_seconds: Optional[int] = None,
        distribution_configuration: Optional["DistributionConfiguration"] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

    def validate(self):
        if self.name is None:
            raise NameError("name is required")
        if self.compute is None:
            raise NameError("compute is required")
        if self._bound_command is None:
            raise NameError("command is required")
        if self.environment is None:
            raise NameError("environment is required for non-local runs")

    def translate_to_rest_object(self) -> CommandJobResource:
        self.bind_inputs()
        self.validate()

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

    def load(self, obj: CommandJobResource):
        properties = obj.properties
        super().load(properties)
        self.name = obj.name
        self.metadata.startTimeUtc = obj.system_data.created_at


class CommandJobSchema(ParameterizedCommandSchema, BaseJobSchema):
    outputs = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())

    @post_load
    def make(self, data, **kwargs):
        return InternalCommandJob(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
