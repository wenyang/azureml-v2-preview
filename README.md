# Azure ML 2.0 Developer Experience
This is the private preview for the Azure ML 2.0 developer experience.

The 2.0 developer platform provides first class API / CLI / SDK support for model training and scoring scenarios.

Private preview launches at the end of November, this repo is in progress.

# Key goals

## New CLI experience
- consistent job story
- consistent endpoint story
- all ML resources, assets and artifacts can be serialized and exported in a human readable format (git-compatible)
- all jobs are now composable
- reduce concepts to fundamentals of: Job, Dataset, Environment, Model, Endpoint, LinkedService (Compute & Storage)

## ARM support
- Improved API surface area and clean APIs for ISVs and language SDKs to build on top of
- ARM for key use cases (job / endpoint creation), including batch scoring endpoints
- Consistent asset management experience (all assets can be registered via ARM now, enforces consistent behavior, etc.)
- Per-resource / per-asset / per-action RBAC and policy support
- X-workspace discovery, consumption and sharing (CI/CD) of assets and resources, proper git-flow support

# Concepts
Note that all schemas are still in the process of being finalized, but the overall structure shouldn't change too much.

**Key Nouns**
- Job
- Dataset
- Environment
- Compute
- Model
- Endpoint

## 	Job (training)
ARM example: https://github.com/mrudulan/DevPlatv2Template

CLI example: ```az ml job create jobspec.yaml```

**Command Job:**
```yaml
name: single_job
run:
  code: ./samples/LightGBM/examples
  command: python ./examples/python-guide/advanced_example.py
  environment:
    name: /Environments/AzureML-LightGBM
compute: goazurego
experiment_name: lightgbm
properties:
  source: repo
```

**Sweep Job:**
```yaml
name: sweep_lightgbm
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
  code: ./samples/LightGBM/examples
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
environment: /Environments/AzureML-LightGBM
```

## Datasets
```bash
az ml dataset create sample.yaml
```

```
name: test
type: AzureBlob
version: "1.0"
description: "this is a test dataset"
linked_service: "./workspaceblobstore"
assetPaths:
  -
    path: "v2test/test.rtf"
    is_directory: False
```

## Environment
```bash
az ml environment create pytorchenv.yaml
```

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

## Compute
```bash
az ml compute create cpucluster.yaml
```

```yaml
type: AzureMLCompute
name: cpu-cluster
min_nodes: 0
max_nodes: 4
sku: STANDARD_D3_V2
```

## -	Model
```bash
az ml model create thismodel.yaml
```

```yaml
name: mymodel
path: ./model
flavors:
  python_function:
    data: model.pkl
    env: conda.yaml
    loader_component: mlflow.sklearn
    python_version: 3.8.2
  sklearn:
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 0.23.1
```

## -	Endpoint (scoring) 

**Real-time**
```yaml
name: myEndpoint
compute: ws:/aks-prod
auth_mode: token
traffic:
  blue: 100

deployments:
  blue:    
    model: ws:/thatmodel:1
    code: ./src/onlinescoring/m1/
    entry_script: ./src/onlinescoring/m1/score.py
    environment: ./src/onlinescoring/env_m1.yaml  
    sku: Standard_FS4_v2
    scale_settings:
      scale_type: auto
      instance_count: 3
      min_instances: 1
      max_instances: 5
    request_settings:
      scoring_timeout_ms: 3000
```

**Batch**
```yaml
name: mnist-sklearn-deployment
endpoint: mnist-sklearn-endpoint
type: Batch
code: ./src
environment: pets-Environment.yaml # or an environment identifier
model: ws:/my-model:1
batch_settings:
  scale_settings:
    node_count: 10 # ? Can we move this up and make it similar to instanceCount in Online?
  partitioning_scheme:
    mini_batch_size: 20
  output_configuration:
    append: row
  error_threshold: 3
  retry_settings:
    timeout_in_seconds: 30

runs-on: ws:/gpu-cluster 
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
