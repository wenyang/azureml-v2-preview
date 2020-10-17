# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from collections import OrderedDict
from marshmallow import (Schema, post_dump, RAISE)
from marshmallow.schema import SchemaMeta
from marshmallow.fields import Nested


class PatchedMeta:
    ordered = True
    unknown = RAISE


class PatchedBaseSchema(Schema):
    class Meta:
        unknown = RAISE
        ordered = True

    @post_dump
    def remove_none(self, data, **kwargs):
        """Prevents from dumping attributes that are None,
        thus making the dump more compact.
        """
        return OrderedDict(
            (key, value) for key, value in data.items()
            if value is not None)

    @post_dump
    def escape_dollars(self, data, **kwargs):
        """
        Escape dollar signs so that loading the schema with variable substitutions will not break.

        during config file loading, variables are expanded, unless the $ character
        is escaped using $$. In the escape case, the escaping $ gets removed, so
        $$var becomes $var. Before serializing this file, we have to add the $
        again, otherwise reading it will fail.
        """

        def repl(val):
            if isinstance(val, str):
                return val.replace('$', '$$')
            if isinstance(val, list):
                # catches list of strings, objects should already be handled if they
                # derive from PatchedBaseSchema
                return list(repl(v) for v in val)
            return val

        return OrderedDict(
            (key, repl(value)) for key, value in data.items()
            if value is not None)


class PatchedSchemaMeta(SchemaMeta):
    """
    Currently there is an open issue in marshmallow, that the "unknown" property
    is not inherited. We use a metaclass to inject a Meta class into all our
    Schema classes.
    """
    def __new__(cls, name, bases, dct):
        meta = dct.get('Meta')
        if meta is None:
            dct['Meta'] = PatchedMeta
        else:
            dct['Meta'].unknown = RAISE
            dct['Meta'].ordered = True

        bases = bases + (PatchedBaseSchema,)
        klass = super().__new__(cls, name, bases, dct)
        return klass


class PatchedNested(Nested):
    """
    anticipates the default coming in next marshmallow version, unknown=True.
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get('unknown') is None:
            kwargs['unknown'] = RAISE
        super().__init__(*args, **kwargs)
