# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


def load_model_params(self):
    with self.argument_context('ml model create') as c:
        c.argument('name', help="The name under which the model should be registered")
        c.argument('version', help="The version id to be set on the version. Any string is allowed, but needs to be unique to the asset, i.e., no two versions of an asset can have the same version.")
        c.argument('file', help="The yaml file containing the entity’s AzureML specification.")
        c.argument('mlflow-folder', help="Instead of –file pointing to an AzureML specification, the user can point to folder containing an MLModel file according to the MLFlow specification. See the MLFlow Model documentation for details")

    with self.argument_context('ml model show') as c:
        c.argument('name', help="Instead of the –id parameter, the name of the resource can be provided to which the operation should be applied.")

    with self.argument_context('ml model list') as c:
        c.argument('filter', help="A filter expression to filter the list of assets returned. we have yet to define the filter expression language to support. On a high level the asset type will be filtered by the noun on which the list operation is executed (e.g. az ml component list). In addition, we will need filtering by name, tags, label, type (in the case of component), creation_context.created_by, creation_context.created_time (range), asset.creation_context.created_by, asset.id, asset.tags, and probably a few more.")
