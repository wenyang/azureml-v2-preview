# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params
from azure.cli.core.commands.parameters import resource_group_name_type


def load_workspace_params(self):
    with self.argument_context("ml workspace list") as c:
        c.argument("resource_group_name", resource_group_name_type)

    with self.argument_context("ml workspace show") as c:
        add_common_params(c)
