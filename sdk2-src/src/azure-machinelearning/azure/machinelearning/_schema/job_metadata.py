# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import (fields, post_load)
from typing import Optional, Dict
import datetime
from .base import PatchedSchemaMeta, PatchedNested
from .interaction_endpoints import InteractionEndpointsSchema
from .._restclient.machinelearningservices.models import JobBaseInteractionEndpoints


class InternalJobMetadata:
    def __init__(
        self,
        *,
        startTimeUtc: Optional[datetime.datetime] = None,
        endTimeUtc: Optional[datetime.datetime] = None,
        tags: Optional[Dict] = None,
        interaction_endpoints: Optional[JobBaseInteractionEndpoints] = None
    ):
        self._startTime = startTimeUtc
        self._endTime = endTimeUtc
        self._tags = tags
        self._interaction_endpoints = interaction_endpoints

    @property
    def startTimeUtc(self) -> datetime.datetime:
        return self._startTime

    @property
    def endTimeUtc(self) -> datetime.datetime:
        return self._endTime

    @property
    def tags(self) -> Dict:
        return self._tags

    @property
    def interaction_endpoints(self) -> JobBaseInteractionEndpoints:
        return self._interaction_endpoints


class JobMetadataSchema(metaclass=PatchedSchemaMeta):
    startTimeUtc = fields.DateTime()
    endTimeUtc = fields.DateTime()
    tags: fields.Dict(values=fields.Str())
    interaction_endpoints = PatchedNested(InteractionEndpointsSchema, dump_only=True)

    @post_load
    def make(self, data, **kwargs) -> InternalJobMetadata:
        return InternalJobMetadata(**data)
