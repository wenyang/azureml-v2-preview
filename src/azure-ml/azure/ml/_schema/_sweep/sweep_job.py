# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Dict

from collections import OrderedDict
from marshmallow import fields, validates, post_load, ValidationError

from azure.ml.constants import PYTHON
from azure.ml._restclient.machinelearningservices.models import CodeConfiguration, EarlyTerminationPolicyConfiguration, \
    EvaluationConfiguration, ParameterSamplingConfiguration, SweepJob, JobBaseResource, TerminationConfiguration, TrialJob
from azure.ml._schema import PatchedNested, CommandJobSchema, InternalCommandJob, \
    PathAwareSchema

from .sweep_limits import SweepLimits, SweepLimitsSchema
from .search_space import HyperparameterExpressionSchema, HyperparameterDistribution
from .sweep_objective import SweepObjectiveSchema
from .sweep_termination import EarlyTerminationSchema


class InternalSweepJob():
    def __init__(
        self,
        *,
        base_path: str = None,
        experiment_name: str = None,
        name: str = None,
        algorithm: str = None,
        search_space: Dict[str, HyperparameterDistribution] = None,
        objective: EvaluationConfiguration = None,
        trial: InternalCommandJob = None,
        early_termination: EarlyTerminationPolicyConfiguration = None,
        limits: SweepLimits = None
    ):
        self._experiment_name = experiment_name
        self._name = name
        self._algorithm = algorithm
        self._search_space = search_space
        self._objective = objective
        self._trial = trial
        self._early_termination = early_termination
        self._limits = limits
        self._base_path = base_path

    @property
    def experiment_name(self) -> str:
        return self._experiment_name

    @experiment_name.setter
    def experiment_name(self, value: str) -> None:
        self._experiment_name = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

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
    def trial(self) -> InternalCommandJob:
        return self._trial

    @trial.setter
    def trial(self, value: InternalCommandJob) -> None:
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

    @property
    def compute(self) -> str:
        return self._compute

    @compute.setter
    def compute(self, value: str) -> None:
        self._compute = value

    @property
    def environment(self) -> str:
        return self._environment

    @environment.setter
    def environment(self, value: str) -> None:
        self._environment = value

    def upload_dependencies(self, code_operations: "CodeOperations"):
        self.trial.upload_dependencies(code_operations)

    def _generate_code_configuration(self) -> CodeConfiguration:
        self.trial.bind_inputs()
        # strip 'python' (if it exists) from command
        self.trial._bound_command = re.sub("(\s*)python(\s*)", "", self.trial._bound_command, 1)
        # remove swept parameters from command
        for param in self.search_space:
            template = r"(\s*)--" + param + r" \{search_space." + param + r"\}(\s*)"
            self.trial._bound_command = re.sub(template, "", self.trial._bound_command)
        return self.trial.generate_code_configuration()

    def translate_to_rest_object(self) -> JobBaseResource:
        parameter_space = {param: dist.translate_to_hyperdrive_param() for (param, dist) in self.search_space.items()}
        parameter_sampling_config = ParameterSamplingConfiguration(parameter_space=parameter_space,
                                                                   sampling_type=self.algorithm.lower().capitalize())
        termination_config = TerminationConfiguration(max_total_runs=self.limits.max_total_runs,
                                                      max_concurrent_runs=self.limits.max_concurrent_runs,
                                                      max_duration_minutes=self.limits.max_duration_minutes,
                                                      early_termination_policy_configuration=self.early_termination)
        trial_job = TrialJob(code_configuration=self._generate_code_configuration(),
                             environment_id=self.trial.environment,
                             data_bindings=self.trial._data_bindings)
        sweep_job = SweepJob(experiment_name=self.experiment_name,
                             compute_binding=self.trial.compute,
                             parameter_sampling_configuration=parameter_sampling_config,
                             termination_configuration=termination_config,
                             evaluation_configuration=self.objective,
                             trial_job=trial_job)
        sweep_job_resource = JobBaseResource(properties=sweep_job)
        sweep_job_resource.name = self.name
        return sweep_job_resource


# This is meant to match the yaml definition NOT the models defined in _restclient
class SweepJobSchema(PathAwareSchema):
    experiment_name = fields.Str(required=False)
    name = fields.Str()
    algorithm = fields.Str()
    search_space = fields.Dict(keys=fields.Str(),
                               values=PatchedNested(HyperparameterExpressionSchema()))
    objective = PatchedNested(SweepObjectiveSchema)
    trial = PatchedNested(CommandJobSchema)
    early_termination = PatchedNested(EarlyTerminationSchema)
    limits = PatchedNested(SweepLimitsSchema)

    @post_load
    def make(self, data, **kwargs):
        return InternalSweepJob(**data)

    @validates("trial")
    def validate_trial_command(self, data, **kwargs):
        if isinstance(data, OrderedDict):
            command = data["command"]
        else:
            command = data.command
        if not command.startswith(PYTHON + " "):
            raise ValidationError("Specified command in trial does not start with python")
