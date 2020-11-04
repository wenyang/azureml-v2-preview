---
title: README
slug: /userguide/
---

Welcome to the AML User Guide!

# Install the CLI
We have pre-built the Azure ML CLI as part of this Git repository. Simply run the following commands to set up your CLI environment

```bash
wget https://github.com/Azure/azureml-v2-preview/suites/1447370079/artifacts/24618504
tar xvf {cli.zip} -C ./azureml2/cli
set AZURE_EXTENSION_DIR=path/you/downloaded/to
az ml -h
```

This should show off the new set of AZ CLI commands and you'll be all set to get started.
