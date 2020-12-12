# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from knack.help_files import helps


def get_job_help():
    helps[
        "ml job create"
    ] = """
        type: command
        short-summary: "Create a new job."
    """
    helps[
        "ml job list"
    ] = """
        type: command
        short-summary: "List all jobs in a workspace."
    """
    helps[
        "ml job show"
    ] = """
        type: command
        short-summary: "Show detail of a job."
    """
    helps[
        "ml job download"
    ] = """
        type: command
        short-summary: "Download job related files into current path."
    """
    helps[
        "ml job stream"
    ] = """
        type: command
        short-summary: "Stream job logs into the console."
    """
    helps['ml job update'] = """
        type: command
        short-summary: "Update job properties and tags."
    """
