---
title: Train Models
---

## Overview

A Job is a Resource that specifies all aspects of a computation job. It aggregates 3 things:

1. What to run
2. How to run it
3. Where to run it

A user can execute a job via the cli by executing an `az ml job create` command. The examples below encapsulate how a user might expand their job definition as they progress with their work.

## A minimal Job run locally

First, the user would just execute a simple command to see if python is working and what packages are available in the environment -- here just `pip freeze`:

```yml
command: pip freeze
code:
  directory: .
environment: azureml:azureml-minimal:1
```

This will be run by executing:
``` cli
> az ml job create --file pipfreezejob.yml
```

## A side-note on tooling

The user is editing the Job yaml file to alter the way the job is run. Job definitions can get very complex, so, to make this easier, we have created JSONSchemas for the Job which can be used in VSCode with the YAML extension. 

Going forward, the VSCode AzureML Extension will add more support, providing code-lenses to lookup compute targets, datasets, components, etc.. 

## Run some real code

Next, let's assume that the data scientist wants to use a pytorch docker image from dockerhub and start by running a python script on it.

```yml
command: python mnist.py
environment: azureml:AzureML-PyTorch-1.6-GPU:44
code: 
  directory: train/pytorch
```

Here's an example that runs on R script:
```yml
command: Rscript test.R
environment: azureml:r-minimal:1
code: 
  directory: train/r
```

## Upload some data to the cloud

Next the input data needs to be moved to the cloud -- therefore the user can create a data artifact in the workspace like so:

```cli
cd ./iris/
az ml data create --file iris-data.yml
```

The above command uploads the data from the local file `.iris/iris.csv` to the `workspaceblobstore` in the folder `/mnistdata`, creates a data entity and registers it under the name `testdata`.

## Use data in your job

In examples/iris, create a job using the base template for iris-job.yml

Envirenment creation via job should work, but seems to not be. So first create environment:

```cli
az ml environment create --file xgboost-env.yml
```
Then submit the job:
```cli
az ml job create --file iris-job.yml --name <unique name>
```

```yml
# yaml-language-server: $schema=https://azuremlsdk2.blob.core.windows.net/latest/commandJob.schema.json
command: >-
  python train.py 
  --data {inputs.training_data} 
environment: azureml:xgboost-env:1
compute:
  target: azureml:<compute-name>
code: 
  directory: train
inputs:
  training_data:
    data: azureml:irisdata:1
    mode: Mount
```

The above job can be run without reference to the dataset, by removing the inputs and the arg in the command, since teh script sets the default value if no data is input. This is to allow further debugging if data store does not work.

## Sweep Job
A Sweep job executes a hyperparameter sweep of a specific search space for a job.

```yml
algorithm: random
job_type: Sweep
name: test10999
experiment_name: ddddddddd
search_space:
  lr:
    spec: uniform
    min_value: 0.001
    max_value: 0.1     
objective:
  primary_metric: accuracy
  goal: maximize
trial:
  command: python ./read_dataset.py --dataset {inputs.value} --lr 0.1
  code: 
    directory: ../python
  environment: azureml:AzureML-PyTorch-1.5-CPU/versions/1
  compute:
    target: azureml:testCompute
  inputs:
    value:
      data: azureml:vnext_test/versions/1
      mode: Mount
limits:
  max_total_runs: 100
  max_concurrent_runs: 10
  max_duration_minutes: 10000
early_termination:
  spec: truncation
  evaluation_interval: 100
  delay_evaluation: 200
  truncation_percentage: 40
  exclude_finished_jobs: True
```

## Other Job Types
Coming soon:
- PipelineJob
- AutoMLJob (s)

```yml
#source ../../../examples/train/basic-command-job/pip_freeze_job.yml
<<<<<<< HEAD:examples/train/basic-command-job/pip_freeze_job.yml
name: pip-freeze-job-example
=======
# yaml-language-server: $schema=https://azuremlsdk2.blob.core.windows.net/latest/commandJob.schema.json
name: test1
>>>>>>> origin:examples/pipfreezejob.yml
command: pip freeze
compute:
  target: azureml:testCompute
#source ../../../examples/train/basic-command-job/pip_freeze_job.yml
```
