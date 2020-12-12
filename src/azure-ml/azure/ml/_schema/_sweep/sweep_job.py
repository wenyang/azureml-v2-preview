# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Dict, Any

from collections import OrderedDict
from marshmallow import fields, validates, post_load, ValidationError

from azure.ml.constants import PYTHON, BASE_PATH_CONTEXT_KEY
from azure.ml._restclient.machinelearningservices.models import (
    CodeConfiguration,
    EarlyTerminationPolicyConfiguration,
    EvaluationConfiguration,
    ParameterSamplingConfiguration,
    SweepJob,
    JobBaseResource,
    TerminationConfiguration,
    TrialJob,
)
from azure.ml._schema import PatchedNested, UnionField

from .sweep_limits import SweepLimits, SweepLimitsSchema
from .search_space import HyperparameterExpressionSchema, HyperparameterDistribution, UniformSchema, ChoiceSchema
from .sweep_objective import SweepObjectiveSchema
from .sweep_termination import EarlyTerminationSchema
from ..job import ParameterizedCommand, TrialJobSchema, BaseJob, BaseJobSchema


class InternalSweepJob(BaseJob):
    def __init__(
        self,
        algorithm: str = None,
        search_space: Dict[str, HyperparameterDistribution] = None,
        objective: EvaluationConfiguration = None,
        trial: ParameterizedCommand = None,
        early_termination: EarlyTerminationPolicyConfiguration = None,
        limits: SweepLimits = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._algorithm = algorithm
        self._search_space = search_space
        self._objective = objective
        self._trial = trial
        self._early_termination = early_termination
        self._limits = limits

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        self._algorithm = value

    @property
    def search_space(self) -> Dict[str, HyperparameterDistribution]:
        return self._search_space

    @search_space.setter
    def search_space(self, value: Dict[str, HyperparameterDistribution]) -> None:
        self._search_space = value

    @property
    def objective(self) -> EvaluationConfiguration:
        return self._objective

    @objective.setter
    def objective(self, value: EvaluationConfiguration) -> None:
        self._objective = value

    @property
    def trial(self) -> ParameterizedCommand:
        return self._trial

    @trial.setter
    def trial(self, value: ParameterizedCommand) -> None:
        self._trial = value

    @property
    def early_termination(self) -> EarlyTerminationPolicyConfiguration:
        return self._early_termination

    @early_termination.setter
    def early_termination(self, value: EarlyTerminationPolicyConfiguration) -> None:
        self._early_termination = value

    @property
    def limits(self) -> SweepLimits:
        return self._limits

    @limits.setter
    def limits(self, value: SweepLimits) -> None:
        self._limits = value

    def upload_dependencies(self, operation_orchestartor: "OperationOrchestrator"):
        self.trial.upload_dependencies(operation_orchestartor)

    def _generate_code_configuration(self) -> CodeConfiguration:
        self.trial.bind_inputs()
        # strip 'python' (if it exists) from command
        self.trial._bound_command = re.sub(r"(\s*)python(\s*)", "", self.trial._bound_command, 1)
        # remove swept parameters from command
        for param in self.search_space:
            template = r"(\s*)--" + param + r" \{search_space." + param + r"\}(\s*)"
            self.trial._bound_command = re.sub(template, "", self.trial._bound_command)
        return self.trial.generate_code_configuration()

    def translate_to_rest_object(self) -> JobBaseResource:
        parameter_space = {param: dist.translate_to_hyperdrive_param() for (param, dist) in self.search_space.items()}
        parameter_sampling_config = ParameterSamplingConfiguration(
            parameter_space=parameter_space, sampling_type=self.algorithm.lower().capitalize()
        )
        termination_config = TerminationConfiguration(
            max_total_runs=self.limits.max_total_runs,
            max_concurrent_runs=self.limits.max_concurrent_runs,
            max_duration_minutes=self.limits.max_duration_minutes,
            early_termination_policy_configuration=self.early_termination,
        )
        trial_job = TrialJob(
            code_configuration=self._generate_code_configuration(),
            environment_id=self.trial.environment,
            data_bindings=self.trial._data_bindings,
        )
        sweep_job = SweepJob(
            experiment_name=self.experiment_name,
            compute_binding=self.trial.compute,
            parameter_sampling_configuration=parameter_sampling_config,
            termination_configuration=termination_config,
            evaluation_configuration=self.objective,
            trial_job=trial_job,
        )
        sweep_job_resource = JobBaseResource(properties=sweep_job)
        sweep_job_resource.name = self.name
        return sweep_job_resource

    def load(self, obj: JobBaseResource):
        properties: SweepJob = obj.properties
        super().load(properties)
        self.name = obj.name
        if hasattr(obj, "system_data") and hasattr(obj.system_data, "created_at"):
            self.metadata.startTimeUtc = obj.system_data.created_at
        self.trial = ParameterizedCommand()
        self.trial.load(properties.trial_job)
        # Compute also appears in both layers of the yaml, but only one of the REST.
        # This should be a required field in one place, but cannot be if its optional in two
        self.trial.compute = properties.compute_binding


# This is meant to match the yaml definition NOT the models defined in _restclient
class SweepJobSchema(BaseJobSchema):
    algorithm = fields.Str()
    search_space = fields.Dict(
        metadata={"values": UnionField([PatchedNested(ChoiceSchema()), PatchedNested(UniformSchema())])},
        keys=fields.Str(),
        values=PatchedNested(HyperparameterExpressionSchema()),
    )
    objective = PatchedNested(SweepObjectiveSchema)
    trial = PatchedNested(TrialJobSchema)
    early_termination = PatchedNested(EarlyTerminationSchema)
    limits = PatchedNested(SweepLimitsSchema)

    @post_load
    def make(self, data, **kwargs):
        return InternalSweepJob(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)

    @validates("trial")
    def validate_trial_command(self, data, **kwargs):
        if isinstance(data, OrderedDict):
            command = data["command"]
        else:
            command = data.command
        if not command.startswith(PYTHON + " "):
            raise ValidationError("Specified command in trial does not start with python")
