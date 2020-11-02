---
title: Cheat Sheet
id: cheatsheet
slug: /cheatsheet/
---

### Basic setup

**Connect to workspace.**

```python
az ml workspace init
a```

For more details: [Workspaces](workspace)

**Connect to compute target.**

```python
from azureml.core import ComputeTarget
target = ComputeTarget(ws, '<compute-target-name>')
```

For more details: [Compute Target](compute-targets)

**Prepare Python environment.**  
You can use a `requirements.txt` file to define a Python environment on your compute.

```yaml
az ml environment create --id pytorchenv --from-pip path/to/requirements.txt
```

You can also use conda environments and docker images to prepare your environments.  

For more details: [Environment](environment)


### Submit code

To run code in AML you need to:

1. **Configure**: Configuration includes specifying the code to run, the compute
target to run on and the Python environment to run in.
2. **Submit**: Create or reuse an AML Experiment and submit the run.

#### ScriptRunConfig (Configure)

A typical directory may have the following structure:

```bash
source_directory/
    script.py    # entry point to your code
    module1.py   # modules called by script.py     
    ...
```

To run `$ (env) python <path/to/code>/script.py [arguments]` on a remote compute cluster `target: ComputeTarget` with an
environment `env: Environment` we use the `ScriptRunConfig` class.

```python
code: <path/to/code>
command: python script.py
compute_target: target
environment: pytorchenv
```

For more details on specifying arguments: [Command line arguments](script-run-config#command-line-arguments)

:::info
- `compute_target`: If not provided the script will run on your local machine **TODO: does this require docker?**
- `environment`: If not provided, uses a default Python environment managed by Azure ML (azureml.core.runconfig.DEFAULT_CPU_IMAGE) **TODO: provide details on this image**.
:::

#### Create Job

```python
az ml job create thejob.yaml
```

This will take you to the Azure ML Studio where you can monitor your run.

For more details: [ScriptRunConfig](script-run-config)

### Connect to data

To work with data in your training scripts using your workspace `ws` and its default datastore:

```python
linked_service_id: ws_default_datastore
path: path/on/datastore>
```

For more details see: [Data](data)
