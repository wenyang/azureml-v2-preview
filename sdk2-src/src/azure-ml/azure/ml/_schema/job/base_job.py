# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields
from typing import Dict, Optional, Any
from ..schema import PatchedNested, PathAwareSchema
from .job_metadata import JobMetadataSchema, InternalJobMetadata
from .loadable_mixin import LoadableMixin


class BaseJob(LoadableMixin):
    def __init__(
        self,
        base_path: Optional[str] = None,
        metadata: InternalJobMetadata = None,
        name: str = None,
        experiment_name: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._base_path = base_path
        self.name = name
        self.metadata = metadata
        self.experiment_name = experiment_name
        self.properties = properties
        self.status = None

    def load(self, obj: Any) -> None:
        super().load(obj)
        self.properties = obj.properties
        self.experiment_name = obj.experiment_name
        try:
            self.metadata = InternalJobMetadata(
                interaction_endpoints=obj.interaction_endpoints)
        except:
            pass
        self.status = obj.status


class BaseJobSchema(PathAwareSchema):
    metadata = PatchedNested(JobMetadataSchema, dump_only=True)
    name = fields.Str()
    status = fields.Str(dump_only=True)
    experiment_name = fields.Str()
    job_type = fields.Str()
    properties = fields.Dict(
        keys=fields.Str(),
        values=fields.Str())
