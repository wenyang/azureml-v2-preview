# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import TypeVar, Generic
from collections import OrderedDict
from pathlib import Path
from azure.ml._utils.utils import load_yaml
from azure.ml.constants import BASE_PATH_CONTEXT_KEY, YAML_FILE_PREFIX
from marshmallow import RAISE, Schema, post_dump, pre_load, post_load, fields
from marshmallow.schema import SchemaMeta


T = TypeVar('T')


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


class PatchedNested(fields.Nested):
    """
    anticipates the default coming in next marshmallow version, unknown=True.
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get('unknown') is None:
            kwargs['unknown'] = RAISE
        super().__init__(*args, **kwargs)


class PathAwareSchema(metaclass=PatchedSchemaMeta):
    def __init__(self, *args, **kwargs):
        self.context = kwargs.get("context", None)
        if self.context is None or self.context.get(BASE_PATH_CONTEXT_KEY, None) is None:
            raise Exception("Base path for reading files is required when building PathAwareSchema")
        super().__init__(*args, **kwargs)


class YamlFileSchema(PathAwareSchema):
    """
    Base class that allows derived classes to be built from paths to separate yaml files in place of inline
    yaml definitions. This will be transparent to any parent schema containing a nested schema of the derived class,
    it will not need a union type for the schema, a YamlFile string will be resolved by the pre_load method
    into a dictionary.
    On loading the child yaml, update the base path to use for loading sub-child files.
    """
    def __init__(self, *args, **kwargs):
        self._previous_base_path = None
        super().__init__(*args, **kwargs)

    @pre_load
    def load_from_file(self, data, **kwargs):
        if isinstance(data, str) and data.startswith(YAML_FILE_PREFIX):
            self._previous_base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
            # Use directly if absolute path
            path = Path(data[len(YAML_FILE_PREFIX):])
            if not path.is_absolute():
                path = self._previous_base_path / path
                path.resolve()
            # Push update
            self.context[BASE_PATH_CONTEXT_KEY] = path.parent
            data = load_yaml(path)
            return data
        return data

    # Schemas are read depth-first, so push/pop to update current path
    @post_load
    def reset_base_path(self, data, **kwargs):
        if self._previous_base_path is not None:
            # pop state
            self.context[BASE_PATH_CONTEXT_KEY] = self._previous_base_path
        return data


class InternalFullSchemaObject(Generic[T]):
    def __init__(self, arm_id: str = None, name: str = None, settings: T = None):
        self.arm_id = arm_id
        self.name = name
        self.settings = settings


def compose_full_schema(child_schema: Schema) -> Schema:
    return Schema.from_dict(
        {
            "arm_id": fields.Str(required=False),
            "name": fields.Str(required=False),
            "settings": PatchedNested(child_schema, required=False)
        },
        name=f"{child_schema.__name__}FullSchema"
    )
