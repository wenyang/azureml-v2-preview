# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def load_dataset_params(self):
    with self.argument_context('ml dataset list') as c:
        c.argument('name', help="Name of the dataset, can be in name:version format. If a version is not provided, all versions of the dataset will be listed.")

    with self.argument_context('ml dataset show') as c:
        c.argument('name', help="Name of the dataset, can be in name:version format. If a version is not provided, the latest version of the dataset will be provided.")

    with self.argument_context('ml dataset create') as c:
        c.argument('name', help="Name of the dataset, can be in name:version format. If a version is not provided, the command will create a dataset with version being latest version + 1")
        c.argument('description', help="Description of the dataset.")
        c.argument('file', help="The yaml file containing definition of the dataset.")

    with self.argument_context('ml dataset delete') as c:
        c.argument('name', help="Name of the dataset, can be in name:version format. If a version is not provided, all versions of the dataset will be deleted.")
