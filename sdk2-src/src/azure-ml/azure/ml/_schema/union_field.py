# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from marshmallow import fields, ValidationError


class UnionField(fields.Field):
    def __init__(
        self,
        schemas: List[fields.Field],
        **kwargs
    ):
        super().__init__(**kwargs)
        self._schemas = schemas

    def _serialize(self, value, attr, data, **kwargs):
        for schema in self._schemas:
            try:
                return schema.serialize(value, attr, data, **kwargs)
            except (TypeError, ValueError) as e:
                # TODO: make error handling more instructive
                continue
        raise ValidationError("Could not deserialize into any of the given schemas")

    def _deserialize(self, value, attr, data, **kwargs):
        errors = []
        for schema in self._schemas:
            try:
                # For nested schema, they should access the true parent, not the union wrapper
                schema.parent = self.parent
                return schema.deserialize(value, attr, data, **kwargs)
            except ValidationError as e:
                errors.append(e.messages)
        raise ValidationError(message=errors, field_name=attr)
