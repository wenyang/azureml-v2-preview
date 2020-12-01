---
title: Train Models
---

## Overview

A Job defines an operation to execute command(s) against a target in a specific virtual environment.
Jobs can be defined in declarative YML and submitted via CLI/SDK/API against durable Azure Resource Manager endpoints.

The key job types in the system are Command Job and Sweep Job (documented below).

CLI example: ```az ml job create --file jobspec.yaml```

## Command Job
Our default Job experience executes a command on a compute target with a set of given inputs.

The below YML file describes the fundamental components of the job specification:
```yaml
name: lightgbm
code: 
  directory: ./samples/LightGBM/examples
command: python ./examples/python-guide/advanced_example.py --lr 0.01 --feature_fraction 0.7 --bagging_fraction 0.6 --data {inputs.data}
environment: azureml:AzureML-Minimal/versions/1
compute: 
  target: azureml:goazurego
  instance_count: 4
inputs:
  data:
    name: azureml:testDirectoryData/versions/1
    mode: Mount
```

## Sweep Job
A Sweep job executes a hyperparameter sweep of a specific search space for a job.

```yaml
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
      name: azureml:vnext_test/versions/1
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
