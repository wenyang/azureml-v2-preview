# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load, ValidationError

from azure.ml._restclient.machinelearningservices.models import (
    BanditPolicyConfiguration,
    MedianStoppingPolicyConfiguration,
    TruncationSelectionPolicyConfiguration,
)
from azure.ml._schema.schema import PatchedSchemaMeta

from .constants import SPEC, BANDIT, MEDIAN, TRUNCATION


class EarlyTerminationSchema(metaclass=PatchedSchemaMeta):
    spec = fields.Str()
    evaluation_interval = fields.Int()
    delay_evaluation = fields.Int()


class BanditPolicyConfigurationSchema(EarlyTerminationSchema):
    slack_factor = fields.Float()
    slack_amount = fields.Float()

    @post_load
    def make(self, data, **kwargs):
        return BanditPolicyConfiguration(**data)


class MedianStoppingPolicyConfigurationSchema(EarlyTerminationSchema):
    @post_load
    def make(self, data, **kwargs):
        return MedianStoppingPolicyConfiguration(**data)


class TruncationSelectionPolicyConfigurationSchema(EarlyTerminationSchema):
    truncation_percentage = fields.Int()
    exclude_finished_jobs = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        return TruncationSelectionPolicyConfiguration(**data)


class EarlyTerminationSchema(metaclass=PatchedSchemaMeta):
    def load(self, data, **kwargs):
        spec = data.pop(SPEC, None)
        if spec == BANDIT:
            return BanditPolicyConfigurationSchema().load(data, **kwargs)
        elif spec == MEDIAN:
            return MedianStoppingPolicyConfigurationSchema().load(data, **kwargs)
        elif spec == TRUNCATION:
            return TruncationSelectionPolicyConfigurationSchema().load(data, **kwargs)
        else:
            raise ValidationError("Early termination policy does not match any of the specified types")
