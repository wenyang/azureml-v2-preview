# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_ml.generated._client_factory import cf_ml_cl
    with self.command_group('ml model', client_factory=cf_ml_cl) as g:
        g.custom_command('create', 'ml_model_create')
        g.custom_command('show', 'ml_model_show')
        g.custom_command('list', 'ml_model_list')

    from azext_ml.generated._client_factory import cf_datastore
    ml_datastore = CliCommandType(
        operations_tmpl='azext_ml.vendored_sdks.machinelearningservices.operations._datastore_operations#DatastoreOpera'
        'tions.{}',
        client_factory=cf_datastore)
    with self.command_group('ml datastore', ml_datastore, client_factory=cf_datastore, is_experimental=True) as g:
        g.custom_command('attach-blob', 'ml_datastore_attach_blob')
        g.custom_command('detach', 'ml_datastore_detach')

    from azext_ml.generated._client_factory import cf_code_version
    ml_code = CliCommandType(operations_tmpl='azext_ml.vendored_sdks.machinelearningservices.operations.'
                                             '_code_version_operations#CodeVersionOperations.{}',
                             client_factory=cf_code_version)
    with self.command_group('ml code', ml_code, client_factory=cf_code_version, is_experimental=True) as g:
        g.custom_command('create', 'ml_code_create')
        g.custom_command('show', 'ml_code_show')
