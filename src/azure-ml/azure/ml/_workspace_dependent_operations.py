# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import yaml
from collections import OrderedDict
from typing import Any, Callable, Optional, cast, Dict

from azure.ml.constants import API_VERSION_2020_09_01_PREVIEW


class WorkspaceScope(object):
    def __init__(self, subscription_id: str, resource_group_name: str, workspace_name: Optional[str]):
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name

    @property
    def subscription_id(self) -> str:
        return self._subscription_id

    @property
    def resource_group_name(self) -> str:
        return self._resource_group_name

    @property
    def workspace_name(self) -> Optional[str]:
        return self._workspace_name

    @workspace_name.setter
    def workspace_name(self, value: str) -> None:
        self._workspace_name = value


def workspace_none_check(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)  # This is to preserve metadata of func
    def new_function(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not self._workspace_scope.workspace_name:
            raise Exception("Please set the default workspace with MLClient.")
        return func(self, *args, **kwargs)

    return new_function


class _WorkspaceDependentOperations(object):
    def __init__(self, workspace_scope: WorkspaceScope):
        self._workspace_scope = workspace_scope
        self._scope_kwargs = {
            'subscription_id': self._workspace_scope.subscription_id,
            'resource_group_name': self._workspace_scope.resource_group_name,
            'api_version': API_VERSION_2020_09_01_PREVIEW
        }
        # Marshmallow supports load/dump of ordered dicts, but pollutes the yaml to tag dicts as ordered dicts
        # Setting these load/dump functions make ordered dict the default in place of dict, allowing for clean yaml
        _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

        def dict_representer(dumper: yaml.Dumper, data) -> yaml.representer.Representer:  # type: ignore
            return dumper.represent_mapping(_mapping_tag, data.items())

        def dict_constructor(loader, node) -> OrderedDict:  # type: ignore
            loader.flatten_mapping(node)
            return OrderedDict(loader.construct_pairs(node))

        # setup yaml to load and dump in order
        yaml.add_representer(OrderedDict, dict_representer)
        yaml.add_constructor(_mapping_tag, dict_constructor, Loader=yaml.SafeLoader)

    @property  # type: ignore
    @workspace_none_check
    def _workspace_name(self) -> str:
        return cast(str, self._workspace_scope.workspace_name)

    @property
    def _subscription_id(self) -> str:
        return self._workspace_scope.subscription_id

    @property
    def _resource_group_name(self) -> str:
        return self._workspace_scope.resource_group_name


class OperationsContainer(object):
    def __init__(self):
        self._all_operations = {}

    @property
    def all_operations(self) -> Dict[str, _WorkspaceDependentOperations]:
        return self._all_operations

    def add(self, name: str, operation: _WorkspaceDependentOperations) -> None:
        self._all_operations[name] = operation
