# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_workspace_help():
    helps[
        "ml workspace"
    ] = """
        type: group
        short-summary: ml workspace
    """
    helps[
        "ml workspace list"
    ] = """
        type: command
        short-summary: "Lists all workspaces in a resource group."
    """
    helps[
        "ml workspace show"
    ] = """
            type: command
            short-summary: "Get the workspace with the specified name."
        """
