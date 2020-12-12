# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


CHUNK_SIZE = 1024
AZ_ML_ARTIFACT_DIRECTORY = "az-ml-artifacts"
UPLOAD_CONFIRMATION = {'upload_status': 'COMPLETED'}
ASSET_PATH_ERROR = "(UserError) Asset paths cannot be updated."
CHANGED_ASSET_PATH_MSG = "The code asset {name}:{version} is already linked to an asset " \
                         "in your datastore that does not match the content from your `directory` param " \
                         "and cannot be overwritten. Please provide a unique name or version " \
                         "to successfully create a new code asset."
