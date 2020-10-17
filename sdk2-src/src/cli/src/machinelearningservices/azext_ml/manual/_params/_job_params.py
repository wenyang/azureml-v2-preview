# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def load_job_params(self):
    with self.argument_context('ml code-job create') as c:
        c.argument('file', help="yaml file to generate code job from")
        c.argument('save_as', help="file to save code job to")
