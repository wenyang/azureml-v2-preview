Overview
============

A Job is a Resource that specifies all aspects of a computation job. It aggregates 3 things:

1. What to run
2. How to run it
3. Where to run it

A user can execute a job via the cli by executing an `az ml job create` command. The examples below encapsulate how a user might expand their job definition as they progress with their work.

A minimal Job run locally
============

First, the user would just execute a simple command to see if python is working and what packages are available in the environment -- here just `pip freeze`:

.. code-block:: yaml
    command: pip freeze
    code:
      directory: .
    environment: azureml:azureml-minimal:1
    compute:
      target: azureml:goazurego

This will be run by executing:

.. code-block:: yaml
    az ml job create --file pipfreezejob.yml


A side-note on tooling
============
The user is editing the Job yaml file to alter the way the job is run. Job definitions can get very complex, so, to make this easier, we have created JSONSchemas for the Job which can be used in VSCode with the YAML extension. 

Going forward, the VSCode AzureML Extension will add more support, providing code-lenses to lookup compute targets, datasets, components, etc.. 

Run some real code
============

Next, let's assume that the data scientist wants to use a pytorch docker image from dockerhub and start by running a python script on it.

.. code-block:: yaml
    command: python mnist.py
    environment: azureml:AzureML-PyTorch-1.6-GPU:44
    code: 
      directory: train/pytorch
    compute:
      target: azureml:goazurego

Here's an example that runs on R script:
.. code-block:: yaml
    command: Rscript test.R
    environment: azureml:r-minimal:1
    code: 
      directory: train/r
    compute:
      target: azureml:goazurego

Upload some data to the cloud
============

Next the input data needs to be moved to the cloud -- therefore the user can create a data artifact in the workspace like so:

.. code-block:: yaml
    cd ./iris/
    az ml data upload -n irisdata -v 1 --path ./data


The above command uploads the data from the local folder `.data/` to the `workspaceblobstore` (default). It creates a data entity and registers it under the name `irisdata`.

Use data in your job
============

In examples/iris, create a job using the base template for iris-job.yml

Envirenment creation via job should work, but if it fails, first create environment:

.. code-block:: yaml
    az ml environment create --file xgboost-env.yml

Then submit the job:

.. code-block:: yaml
    az ml job create --file iris-job.yml --name <unique name> --query metadata.interaction_endpoints.studio

The query parameter will return just the studio url for the run, rather than the entire job object. To view the entire job object,
we can use the CLI to show this job:

.. code-block:: console
    az ml job show <name of previous job>

.. code-block:: yaml
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

The above job can be run without reference to the dataset, by removing the inputs and the arg in the command, since teh script sets the default value if no data is input. This is to allow further debugging if data store does not work.

.. code-block:: yaml
    # yaml-language-server: $schema=https://azuremlsdk2.blob.core.windows.net/latest/commandJob.schema.json
    command: >-
      python train.py
    environment: azureml:xgboost-env:1
    compute:
      target: azureml:<compute-name>
    code: 
      directory: train

Distributed Training
============

Distributed command jobs have a 'distribution' section where you define the distribution type and properties that are unique to distributed training.

MPI based
============

.. code-block:: yaml
name: test1
command: pip freeze
environment: azureml:AzureML-Minimal:1
compute:
  target: azureml:testCompute
  instance_count: 4
distribution:
  type: mpi
  process_count_per_node: 4
experiment_name: mfe_distributed

PyTorch based
============

.. code-block:: yaml
    command: pip freeze
    environment: azureml:AzureML-Minimal:1
    name: test1
    compute:
      target: azureml:testCompute
    distribution:
      type: PyTorch
    experiment_name: mfe-test1
  
Tensorflow based
============

.. code-block:: yaml
    command: pip freeze
    environment: azureml:AzureML-Minimal:1
    name: "test1"
    compute:
      target: azureml:testCompute
    distribution:
      type: TensorFlow
      parameter_server_count: 3
      worker_count: 3
    experiment_name: mfe-test1

  
Sweep Job
============

A Sweep job executes a hyperparameter sweep of a specific search space for a job. The below yaml uses the command job from the previous section as the 'trial' job in the sweep. It sweeps over different learning rates and subsample rates for each child run. The search space parameters will be passed as arguments to the command in the trial job.

.. code-block:: yaml
    experiment_name: iris-sweep-trial
    algorithm: random
    job_type: Sweep
    name: test
    search_space:
      learning-rate:
        spec: uniform
        min_value: 0.001
        max_value: 0.1
      subsample:
        spec: uniform
        min_value: 0.1
        max_value: 1.0    
    objective:
      primary_metric: accuracy
      goal: maximize
    trial:
      command: >-
        python train.py --data {inputs.training_data}
      environment: azureml:xgboost-env:1
      compute:
        target: azureml:<compute-name>
      code: 
        directory: train
      inputs:
        training_data:
          data: azureml:irisdata:1
          mode: Mount
    limits:
      max_total_runs: 10
      max_concurrent_runs: 10
      max_duration_minutes: 20

This can be executed by running (after setting compute name in yaml):

.. code-block:: yaml
    az ml job create --file iris-sweep.yml --name <unique name>


Other Job Types
=============

Coming soon:
- PipelineJob
- AutoMLJob (s)
