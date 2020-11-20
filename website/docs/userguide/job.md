---
title: Train Models
---

## Overview

A Job defines an operation to execute command(s) against a target in a specific virtual environment.
Jobs can be defined in declarative YML and submitted via CLI/SDK/API against durable Azure Resource Manager endpoints.

The key job types in the system are Command Job and Sweep Job (documented below).

CLI example: ```az ml job create jobspec.yaml```

**Command Job:**
```yaml
name: lightgbm
code: ./samples/LightGBM/examples
run: python ./examples/python-guide/advanced_example.py --lr 0.01 --feature_fraction 0.7 --bagging_fraction 0.6 --data {inputs.the_data}
container: { image: microsoft/lightgbm }
runs-on: 
  target: azureml:goazurego
  node_count: 4
inputs:
  the_data: 
    from: blob/uri
    mode: mount
```

**Sweep Job:**
```yaml
name: sweep_lightgbm
algorithm: random
search_space:
  lr:
    spec: uniform
    min_value: 0.01
    max_value: 0.1
objective:
  primary_metric: rmse
  goal: minimize
trial: 
  run: python ./examples/python-guide/advanced_example.py  --lr {search_space.lr} --feature_fraction 0.7 --bagging_fraction 0.6
  code: ./samples/LightGBM/examples
  container: { image: microsoft/lightgbm }
early_termination:
  spec: median
  evaluation_interval: 1
  delay_evaluation: 5
runs-on: goazurego
```
