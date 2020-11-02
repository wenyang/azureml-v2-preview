---
title: Job
---

## Overview

A Job...

CLI example: ```az ml job create jobspec.yaml```

**Command Job:**
```yaml
name: lightgbm
run:
  code: ./samples/LightGBM/examples
  command: python ./examples/python-guide/advanced_example.py --lr 0.01 --feature_fraction 0.7 --bagging_fraction 0.6
  environment:
    name: lightgbm
compute: goazurego
properties:
  source: repo
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
  command: python ./examples/python-guide/advanced_example.py  --lr {search_space.lr} --feature_fraction 0.7 --bagging_fraction 0.6
  code: ./samples/LightGBM/examples
  environment: lightgbm
early_termination:
  spec: median
  evaluation_interval: 1
  delay_evaluation: 5
compute: goazurego
```
