# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List
import copy
from marshmallow import fields, ValidationError
from marshmallow.utils import resolve_field_instance, FieldInstanceResolutionError


class UnionField(fields.Field):
    def __init__(self, union_fields: List[fields.Field], **kwargs):
        super().__init__(**kwargs)
        try:
            # add the validation and make sure union_fields must be subclasses or instances of
            # marshmallow.base.FieldABC
            self._union_fields = [resolve_field_instance(cls_or_instance) for cls_or_instance in union_fields]
        except FieldInstanceResolutionError as error:
            raise ValueError(
                'Elements of "union_fields" must be subclasses or ' "instances of marshmallow.base.FieldABC."
            ) from error

    # This sets the parent for the schema and also handles nesting.
    def _bind_to_schema(self, field_name, schema):
        super()._bind_to_schema(field_name, schema)
        new_union_fields = []
        for field in self._union_fields:
            field = copy.deepcopy(field)
            field._bind_to_schema(field_name, self)
            new_union_fields.append(field)

        self._union_fields = new_union_fields

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None

        for field in self._union_fields:
            try:
                return field._serialize(value, attr, obj, **kwargs)
            except (TypeError, ValueError, ValidationError):
                # TODO: make error handling more instructive
                continue
        raise ValidationError("Could not deserialize into any of the given schemas")

    def _deserialize(self, value, attr, data, **kwargs):
        errors = []
        for schema in self._union_fields:
            try:
                return schema.deserialize(value, attr, data, **kwargs)
            except ValidationError as e:
                errors.append(e.messages)
        raise ValidationError(message=errors, field_name=attr)
