# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
from typing import Any, Callable, Optional, cast


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
            raise Exception("Please set the default workspace with MachineLearningClient.")
        return func(self, *args, **kwargs)

    return new_function


class _WorkspaceDependentOperations(object):
    def __init__(self, workspace_scope: WorkspaceScope):
        self._workspace_scope = workspace_scope

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
