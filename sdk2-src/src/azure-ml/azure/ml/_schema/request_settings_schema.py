# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any
from marshmallow import fields, post_load
from .schema import PatchedBaseSchema


class InternalRequestSettings:
    def __init__(self,
                 request_timeout_ms: int = None,
                 max_concurrent_requests_per_instance: int = None,
                 max_queue_wait_ms: int = None):
        self._request_timeout_ms = request_timeout_ms
        self._max_concurrent_requests_per_instance = max_concurrent_requests_per_instance
        self._max_queue_wait_ms = max_queue_wait_ms

    @property
    def request_timeout_ms(self):
        return self._request_timeout_ms

    @property
    def max_concurrent_requests_per_instance(self):
        return self._max_concurrent_requests_per_instance

    @property
    def max_queue_wait_ms(self):
        return self._max_queue_wait_ms


class RequestSettingsSchema(PatchedBaseSchema):
    request_timeout_ms = fields.Int(required=False)
    max_concurrent_requests_per_instance = fields.Int(required=False)
    max_queue_wait_ms = fields.Int(required=False)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> InternalRequestSettings:
        return InternalRequestSettings(**data)
