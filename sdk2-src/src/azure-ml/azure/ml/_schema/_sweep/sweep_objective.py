# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ml._schema.schema import PatchedSchemaMeta
from azure.ml._restclient.machinelearningservices.models import EvaluationConfiguration


class SweepObjectiveSchema(metaclass=PatchedSchemaMeta):
    primary_metric_goal = fields.Str(data_key="goal")
    primary_metric_name = fields.Str(data_key="primary_metric")

    @post_load
    def make(self, data, **kwargs):
        return EvaluationConfiguration(**data)
