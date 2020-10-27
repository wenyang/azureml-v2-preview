# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):
    from azext_ml.generated._client_factory import cf_ml_cl
    with self.command_group('ml model', client_factory=cf_ml_cl, is_experimental=True) as g:
        g.custom_command('create', 'ml_model_create')
        g.custom_command('show', 'ml_model_show')
        g.custom_command('list', 'ml_model_list')

    with self.command_group('ml environment', client_factory=cf_ml_cl, is_experimental=True) as g:
        g.custom_command('create', 'ml_environment_create')
        g.custom_command('show', 'ml_environment_show')
        g.custom_command('list', 'ml_environment_list')

    with self.command_group('ml dataset', client_factory=cf_ml_cl, is_experimental=True) as g:
        g.custom_command('create', 'ml_dataset_create')
        g.custom_command('show', 'ml_dataset_show')
        g.custom_command('list', 'ml_dataset_list')
        g.custom_command('delete', 'ml_dataset_delete')

    with self.command_group('ml code', client_factory=cf_ml_cl, is_experimental=True) as g:
        g.custom_command('create', 'ml_code_create')
        g.custom_command('show', 'ml_code_show')

    from azext_ml.generated._client_factory import cf_datastore
    ml_datastore = CliCommandType(
        operations_tmpl='azext_ml.vendored_sdks.machinelearningservices.operations._datastore_operations#DatastoreOpera'
        'tions.{}',
        client_factory=cf_datastore)
    with self.command_group('ml datastore', ml_datastore, client_factory=cf_datastore, is_experimental=True) as g:
        g.custom_command('attach-blob', 'ml_datastore_attach_blob')
        g.custom_command('detach', 'ml_datastore_detach')
