# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._common_params import add_common_params


def load_compute_params(self):
    with self.argument_context('ml compute list') as c:
        add_common_params(c)

    with self.argument_context('ml compute show') as c:
        add_common_params(c)
        c.argument('name', help="Name of the compute resource, required.")
