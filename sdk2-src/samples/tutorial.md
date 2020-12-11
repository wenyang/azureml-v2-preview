
## Get set up

1. Create a workspace in _Vienna Personal 1_ subscription, in the master region.

1. [Optional] Install the cli extension for typeahead with yaml
   - download from https://microsoft-my.sharepoint.com/:u:/p/rihorn/EZaVuJ4tmGRAotD9MXiQU5YBr7edXnMeLYCm0o3TL0xLaQ?e=mtzg02
    - unzip in $Users/< alias >/.vscode/extensions/
   - restart VS Code to take effect
   - File names should be of form *-CommandJob.yaml, see in package.json in extension for complete list

1. Install the CLI:

   - If you previously set the *AZURE_EXTENSION_DIR* environment variable, unset it. The new installation steps below may conflict with a prior installation.
   - Uninstall any existing AzureML CLI extensions:
     - Run `az extension list` to show the extensions you have installed.
     - Uninstall any AzureML extensions with `az extension remove --name <extension-name-to-remove>`
   - Install the CLIv2 extension: `az extension add --source https://azuremlsdktestpypi.blob.core.windows.net/wheels/sdk-cli-v2/26401099/ml-0.0.2-py3-none-any.whl --pip-extra-index-urls https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2/26401099`
   - Confirm that the extension is installed correctly: `az ml job create -h` should produce a usable output, and you should see a `--file` argument.

1. Set some defaults:
  - az account set -s \<my-subscription-id>
  - az configure --defaults group=\<my-resource-group>
  - az configure --defaults workspace=\<my-workspace>
  -  Optional: To change the default output format to yaml, run `az configure` and use the interactive guide.

# Create a CommandJob

Run the commands below to create a command job. Most commands take a yaml file as input. *You must edit each file before submitting it*. The directions walk you through the process of editing the first file.

## Create a data asset

  Create a data asset for your command job to consume. You must provide a name and version, like "newdata:1".

  `az ml data upload --name <data-asset-name>:<version> --path ..\python\sample1.csv`

  and show the dataset you just created:

  `az ml data show --name <data-asset-name>:<version>`

## Create a command job

1.  Open code_job.yaml and make several changes:

   - Set the job name. Each job must have a unique name in your workspace.
   - Update the environment string: set the subscription ID, resource group, workspace name, and environment name. The version string is required.
   - Update the input string: set the subscription ID, resource group, workspace name, and data asset name, and version.
   - Set the name of your compute cluster. You can list the computes in your workspace with `az ml compute list`.

1. Submit the job: `az ml job create --file code_job.yml`.

1. Stream the logs for your new job: `az ml job stream --name <my-job-name>`

1. View the job in the Studio: `az ml job show --name <my-job-name>` and find the Studio URL (under Properties->interactionEndpoints).

1. Download the job logs to your current directory: `az ml job download --name <my-job-name>`.

You can also list your jobs with `az ml job list`.

## Create a SweepJob

Open sweep_from_command_job.yaml. Update the environment, input, compute cluster, name, and experiment name. Then submit your sweep job: `az ml job create --file sweep_from_command_job.yaml`.

You can view the job in the Studio to see its child runs.

## Create a registered model

First, create a registered model. We'll use a model I've already downloaded for this tutorial. Open model.yml and update the environment. You must also provide a model name and model version. Then create the model asset with `az ml model create --file model.yml`. You can also *list* and *show* models.

## Environment

Create an environment `az ml environment create --file environment_conda.yml --name <environment_name>`

Bonus : Try creating environment using environment_docker.yml, environment_python.yml

Show an environment `az ml environment show --name <envrionment_name>`

List environments `az ml environment list`

Create new version of existing environment
  1. Update the version in yaml file (should be latest version + 1)
  2. Update conda file (environment.yml) in environment_files
  3. Run `az ml environment create --file environment_conda.yml --name <environment_name>`
