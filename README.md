# Azure ML 2.0 Developer Experience
This is the private preview for the Azure ML 2.0 developer experience.

The 2.0 developer platform provides first class API / CLI / SDK support for model training and scoring scenarios.

# Key goals

## New CLI experience
- consistent progression from simple job to sweep job to workflow  job
- consistent progression from model to endpoint (real time and batch)
- all ML resources, assets and artifacts can be serialized and exported in a human readable format (git-compatible)
- support for reusable Components - all jobs are now composable
- reduce concepts to fundamentals of: Job, Component, Data, Environment, Model, Endpoint, LinkedService (aka AttachedResource)

## ARM support
- Improved API surface area and clean APIs for ISVs and language SDKs to build on top of
- ARM for key use cases (job / endpoint creation), including batch scoring endpoints
- Consistent asset management experience (all assets can be registered via ARM now, enforces consistent behavior, etc.)
- Per-resource / per-asset / per-action RBAC and policy support
- X-workspace discovery, consumption and sharing (CI/CD) of assets and resources, proper git-flow support

# Concepts

## 	Job (training)
To run a job, execute the following cli command: ```az ml job create jobspec.yaml```

**Command Job:**
```yaml
run:
  code: ./samples/LightGBM/examples
  command: python ./examples/python-guide/advanced_example.py
  environment:
    name: /subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/paulshmaster2/providers/Microsoft.MachineLearningServices/Environments/AzureML-AutoML-DNN-GPU
name: single_job
on_compute:
  target: goazurego
experiment_name: lightgbm
properties:
  source: repo
```

**Sweep Job:**
```yaml
experiment_name: lightgbm
algorithm: random
search_space:
  --lr:
    spec: uniform
    min_value: 0.01
    max_value: 0.1
  --feature_fraction:
    spec: uniform
    min_value: 0.7
    max_value: 0.9
  --bagging_fraction:
    spec: uniform
    min_value: 0.6
    max_value: 0.8     
objective:
  primary_metric: rmse
  goal: minimize
trial: 
  command: python ./examples/python-guide/advanced_example.py
  code: C:\Users\paulsh\Documents\sdk-cli-v2\samples\LightGBM\examples
limits:
  max_total_runs: 10
  max_concurrent_runs: 5
  max_duration_minutes: 10000
early_termination:
  spec: bandit
  evaluation_interval: 100
  slack_factor: 0.2
  delay_evaluation: 200
compute: goazurego
environment: /subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/paulshmaster2/providers/Microsoft.MachineLearningServices/Environments/AzureML-AutoML-DNN-GPU
```

## Datasets
```
name: testDataset
version: "1.0"
description: "this is a test dataset"
linkedServiceId: "/subscriptions/5f08d643-1910-4a38-a7c7-84a39d4f42e0/resourceGroups/sdk_vnext_cli/providers/Microsoft.MachineLearningServices/workspaces/sdk_vnext_cli/workspaceblobstore"
assetPaths:
  -
    path: "v2test/test.rtf"
    is_directory: False
```

## Environment

```
name: AzureML-Pytorch
version: '1'
docker:
   image: mcr.microsoft.com/azureml/base:0.2.2
conda:
   inline:
      name: "test_env"
      channels:
         - conda-forge
      dependencies:
         - python=3.6.2
         - pip:
            - azureml-defaults
            - torch
            - torchvision
            - fastai
      prefix: "aml"
   interpreter_path: "python" # defaults to python

```

## -	Compute
Coming soon

## -	Model
Coming soon

## -	Endpoint (scoring) 
Coming soon

## Run a job in 2.0 (CLI)

> Note: The CLI is handling upload and registration of local assets (code / data) as required. Upload and download will leverage Azure Storage recommended solution, eg. az storage 

## Run a job in 2.0 (REST API)

Here we see the relevate section of the ARM template (and REST API) to achive the same as shown above.

```json 
PUT .../providers/Microsoft.MachineLearningServices/workspaces/my_ws/jobs/great_job_007

{
  ...
  "properties": {
    "run": {
      "command": "python train.py  --data $AZUREML_DATASET_inputs.data  --epochs 14 --batch-size 64 --test-batch-size 1000 --lr 1.0 --gamma 0.7 --save_model outputs/model",
      "environment": {
        "docker": {
          "image": "pytorch/pytorch"
        }
      },
      "code": {
        "id": "eff289b6-416f-41f0-8a8b-7aa5e5d154bf"
      }
    },
    "inputs": {
      "data": {
        "mount": "mnist-data"
      }
    }
  }
}
```

> Note: The REST API requires the user to first upload and register their code/assets before calling the job create API. Also in the command line, parameters need to be replaced before sending it to the REST API. 



## Current Timeline

November 2020 (committed): 
  - Cloud execution of job (command job and sweep job)
  - Support for Data / Code / Environment / Model assets in jobs

March 2021 (pending):
- Private preview of full feature set of end2end training flow captured in [private preview 2](specs/job.md)
 -- including the above plus:
  - local docker training (w/ local + data)
  - spark job support
  - Workflow - full support & alignment with jobs
  - Real time and batch Endpoint
