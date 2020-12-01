# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params, add_override_param


def add_job_common_params(c):
    c.argument('name', help="Name of the job.")


def load_job_params(self):
    with self.argument_context('ml job create') as c:
        add_common_params(c)
        add_job_common_params(c)
        add_override_param(c)
        c.argument('file', help="yaml file to generate code job from.")
        c.argument('save_as', help="file to save code job to.")
        c.argument('stream', help="streams the job logs into the console.")

    with self.argument_context('ml job list') as c:
        add_common_params(c)

    with self.argument_context('ml job show') as c:
        add_common_params(c)
        add_job_common_params(c)

    with self.argument_context('ml job download') as c:
        add_common_params(c)
        add_job_common_params(c)
        c.argument('outputs', help="All files generated in the job including outputs.")
        c.argument('download_path', help="If not specified will be downloaded into the current dir.")

    with self.argument_context('ml job stream') as c:
        add_common_params(c)
        add_job_common_params(c)
