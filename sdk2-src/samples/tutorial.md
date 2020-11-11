
## Get set up

1. Create a workspace in _Vienna Personal 1_ subscription, in the master region.

1. Install the CLI:

   - Pull the docker image: `docker pull mossaka/sdk_cli_v2_bug_bash`
   - Run the docker container: `docker run --rm -it mossaka/sdk_cli_v2_bug_bash:latest`
   - Activate conda: `conda activate myenv`
   - Confirm that az cli is installed by running `az -h`
   - Install the SDK:
     - `pip install --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2 azure-ml==0.0.1`
     - Verify: `python -c "from azure.ml import MLClient"`
   - Install the CLI: 
     - Download the custom wheel: `curl https://paulshaml18829289173.blob.core.windows.net/wheels/ml-0.1.0-py3-none-any.whl -o ml-0.1.0-py3-none-any.whl`
     - Install the CLI: `az extension add --source ml-0.1.0-py3-none-any.whl`
     - Confirm that you are set up: `az ml -h`. 

1. In your container terminal, run `cd ~`. 

1. Connect to your container with VSCode:
   - Install the "Remote - Development" extension.
   - Click on the "Remote Explorer" pane on the left
   - Choose "Containers" at the top (default is "WSL Targets")
   - right-click on your running container and choose "Attach to Container"
   - Open the directory */home/yaml* if it does not open by default.

1. Set some defaults:
  - az account set -s <<my-subscription-id>
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

You can also list your jobs.

## Create a SweepJob

Open sweep_from_command_job.yaml. Update the environment, input, compute cluster, name, and experiment name. Then submit your sweep job: `az ml job create --file sweep_from_command_job.yaml`.

You can view the job in the Studio to see its child runs.

## Create an endpoint

First, create a registered model. We'll use a model I've already downloaded for this tutorial. Open model.yml and update the environment. You must also provide a model name and model version. Then create the model asset with `az ml model create --file model.yml`. You can also *list* and *show* models.

Next, create an endpoint that uses the model. Open endpoint.yaml and update the model and environment. Give the endpoint a name. Set *infrastructure* to the name of an AKS cluster in your workspace. Then deploy the endpoint: `az ml endpoint create --file endpoint.yaml`. You can also *show* and *delete* the endpoint.

## Other things to try

1. Create en environment: `az ml environment create --file environment.yml` (Paul to update the sample)