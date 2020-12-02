```
az ml job create traintorch.yml

traintorch.yml
inputs:
  mnist: 
    path: https://azureopendatastorage.blob.core.windows.net/mnist/
command: >-
    python train.py
    --data { inputs.mnist }
    --epochs 14
    --batch-size 64
    --test-batch-size 1000
    --lr 1.0
    --gamma 0.7
container: 
  image: pytorch/pytorch
code: ./src
compute: 
  target: cpu-cluster
  node_count: 4
  distributed: 
    type: mpi
    process_count_per_node: 4
```

// sweep this job //
```
az ml job create sweepjob.yml

name: sweep-job-example
algorithm: random
search_space:
  lr:
    type: uniform
    min_value: 0.001
    max_value: 0.1
  conv_size:
    type: choice
    values: [2, 5, 7]
  dropout_rate:
    type: uniform
    min_value: 0.1
    max_Value: 0.5     
objective:
  primary_metric: accuracy
  goal: maximize
trial: 
  name: a_trial 
  command: python train.py --epochs 500 --lr { search_space.lr } --dropout-rate { search_space.dropout_rate } --conv-size { search_space.conv_size }
  environment: azureml:Environments/AzureML-Minimal
  compute:
    target: azureml:Compute/test-cluster
early_termination:
  type: bandit
  evaluation_interval: 100
  slack_factor: 0.2
  delay_evaluation: 200
limits:
  max_total_trials: 100
  max_concurrent_trials: 10
  timeout_minutes: 10000
    
```

 // workflow job - NOT IMPLEMENTED
```
type: TBD
inputs: 
  previous_run_id: 
    type: string
    default: guid1
strategy:
  max-parallel: 4
  matrix:
    language: [ english, spanish, french, mandarin, latinv2 ]
    styles: [ printed, mixed ]
jobs:
  prep:
   command: python prep.py --language {inputs.language_data} --language --styles {matrix.styles} --resume_from {inputs.previous_run_id}
   code: ./src
   target: cpu
   inputs:
     language_data: 
       path: azureml:Datasets/ocr_data/[matrix.language]
   train:
     target: gpu
     command: python train.py --data {jobs.prep.outputs.prepped_data}
     code: ./src
     
```
