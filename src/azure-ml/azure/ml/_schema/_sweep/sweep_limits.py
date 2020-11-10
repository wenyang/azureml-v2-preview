# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import cast, Optional

from marshmallow import (fields, post_load)

from azure.ml._schema.schema import PatchedSchemaMeta


class SweepLimits():
    def __init__(
        self,
        *,
        max_concurrent_runs: Optional[int] = None,
        max_duration_minutes: Optional[float] = None,
        max_total_runs: Optional[int] = None
    ):
        self._max_concurrent_runs = max_concurrent_runs
        self._max_duration_minutes = max_duration_minutes
        self._max_total_runs = max_total_runs

    @property
    def max_concurrent_runs(self) -> int:
        return cast(int, self._max_concurrent_runs)

    @max_concurrent_runs.setter
    def max_concurrent_runs(self, value: int) -> None:
        self._max_concurrent_runs = value

    @property
    def max_duration_minutes(self) -> float:
        return cast(float, self._max_duration_minutes)

    @max_duration_minutes.setter
    def max_duration_minutes(self, value: float) -> None:
        self._max_duration_minutes = value

    @property
    def max_total_runs(self) -> int:
        return cast(int, self._max_total_runs)

    @max_total_runs.setter
    def max_total_runs(self, value: int) -> None:
        self._max_total_runs = value


class SweepLimitsSchema(metaclass=PatchedSchemaMeta):
    max_total_runs = fields.Int(required=False)
    max_concurrent_runs = fields.Int(required=False)
    max_duration_minutes = fields.Float(required=False)

    @post_load
    def make(self, data, **kwargs):
        return SweepLimits(**data)
