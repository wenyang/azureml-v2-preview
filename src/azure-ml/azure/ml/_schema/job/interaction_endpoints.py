# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load
from ..schema import PatchedSchemaMeta
from azure.ml._restclient.machinelearningservices.models import JobBaseInteractionEndpoints


class InteractionEndpointsSchema(metaclass=PatchedSchemaMeta):
    studio = fields.Str()
    grafana = fields.Str()
    tensorboard = fields.Str()
    tracking = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        return JobBaseInteractionEndpoints(**data)
