---
title: Running Code in the Cloud
---

## Job

A common way to run code in the cloud is via a Job which executes a command against a provided working directory, in a provided 

Consider the following layout for your code.

```bash
source_directory/
    script.py    # entry point to your code
    module1.py   # modules called by script.py     
    ...
```

To run `script.py` in the cloud via the `ScriptRunConfig`

```python
code: <path/to/source_directory>
command: script.py --learning_rate 0.001 --momentum 0.9
compute_target: target
environment: env_name
```

where:

- `code` : Local directory with your code.
- `command` : Script to run. This does not need to be at the root of `source_directory`.
- `compute_taget` : See [Compute Target](copute-target)
- `environment` : See [Environment](environment)

## Command

### Example: `sys.argv`

In this example we pass two arguments to our script. If we were running this from the
console:

```console title="console"
$ python script.py 0.001 0.9
```

This can be consumed as usual in our script:

```python title="script.py"
import sys
learning_rate = sys.argv[1]     # gets 0.001
momentum = sys.argv[2]          # gets 0.9
```

### Example: `argparse`

In this example we pass two named arguments to our script. If we were running this from the
console:

```console title="console"
$ python script.py --learning_rate 0.001 --momentum 0.9
```

which can be consumed as usual in our script:

```python title="script.py"
import argparse
parser = argparse.Argparser()
parser.add_argument('--learning_rate', type=float)
parser.add_argument('--momentum', type=float)
args = parser.parse_args()

learning_rate = args.learning_rate      # gets 0.001
momentum = args.momentum                # gets 0.9
```

## Using Datasets

### via Arguments

Pass a dataset to your ScriptRunConfig as an argument

```yaml
data: { linked_service_id: ws_default_storage, path: <path/on/datastore> }
command: python script.py --dataset {inputs.data}
```

This mounts the dataset to the run where it can be referenced by `script.py`.
