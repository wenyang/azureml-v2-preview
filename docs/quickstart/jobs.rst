Running Jobs
============

To Organize
-----------

Hello world
~~~~~~~~~~~

Create your first job
~~~~~~~~~~~~~~~~~~~~~

Prepare the code you'd like to run. For this example, we'll simply clone the v2 preview repo and run the first example!

.. code-block:: console

    git clone https://github.com/Azure/azureml-v2-preview

.. note:: To authenticate the git clone, you may need a PAT. You can generate one here: https://github.com/settings/tokens (use anything as username, the PAT as your password)**

Check that a compute cluster exists in your workspace and the name (goazurego) matches the one specified in the https://github.com/Azure/azureml-v2-preview/examples/commandjob.yml file. If you used the ARM template, this will be set up for you. Submit your first job using the job create command. You should see a new run from the Studio UI (https://ml.azure.com) Home page or Experiments page. 

.. code-block:: console

    az ml job create --file azureml-v2-preview/examples/train/basic-command-job/pip_freeze_job.yml

Understanding commandjob.yml and az ml job create
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A few interesting things to note about the yaml file:

.. code-block:: yaml

    name: test1
    compute:
        target: azureml:goazurego
    command: /bin/sh -c 'pip freeze && echo hello world'
    environment: azureml:AzureML-Minimal:1
    code:
        directory: .

- 'name' is the user defined run name which needs to be **unique**. By default, runs are created in an Experiment called "Default". If you want to use a different experiment name, you can use the parameter experiment_name.
- 'name' and other parameters can be overwritten from the command line. For example: az ml job create --file azureml-v2-preview/examples/commandjob.yml --name test2
- 'directory' path is relative to where the yaml file exists, not where the command is being run from.
- All the files from 'directory' are uploaded as snapshot before the job is created and can be viewed in the Snapshot page of the run from Studio UI.
- 'azureml' is a special moniker used to refer to an existing entity within the workspace. In this case 'azureml:AzureML-Minimal:1' is expecting that version 1 of an environment called AzureML-Minimal exists in the current workspace. Similarly, 'azureml:testCompute' refers to a compute cluster called 'testCompute' in the current workspace. 
- 'command' parameter refers to the command that gets run on the remote compute. This usually gets replaced by the relevant training command, example: "python train.py" or "Rscript train.R".

A Job is a Resource that specifies all aspects of a computation job. It aggregates 3 things:

1. What to run
2. How to run it
3. Where to run it

A user can execute a job via the cli by executing an `az ml job create` command. The examples below encapsulate how a user might expand their job definition as they progress with their work.

A minimal Job run locally
-------------------------

First, the user would just execute a simple command to see if python is working and what packages are available in the environment -- here just `pip freeze`:

.. code-block:: yaml

    command: pip freeze
    code:
      directory: .
    environment: azureml:azureml-minimal:1
    compute:
      target: azureml:goazurego

This will be run by executing:

.. code-block:: console

    az ml job create --file pipfreezejob.yml


A side-note on tooling
----------------------

The user is editing the Job yaml file to alter the way the job is run. Job definitions can get very complex, so, to make this easier, we have created JSONSchemas for the Job which can be used in VSCode with the YAML extension. 

Going forward, the VSCode AzureML Extension will add more support, providing code-lenses to lookup compute targets, datasets, components, etc.. 

Run some real code
------------------

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
-----------------------------

Next the input data needs to be moved to the cloud -- therefore the user can create a data artifact in the workspace like so:

.. code-block:: console

    cd ./iris/
    az ml data upload -n irisdata -v 1 --path ./data


The above command uploads the data from the local folder `.data/` to the `workspaceblobstore` (default). It creates a data entity and registers it under the name `irisdata`.

Use data in your job
--------------------

In examples/iris, create a job using the base template for iris-job.yml

Envirenment creation via job should work, but if it fails, first create environment:

.. code-block:: console

    az ml environment create --file xgboost-env.yml

Then submit the job:

.. code-block:: console

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
--------------------

Distributed command jobs have a 'distribution' section where you define the distribution type and properties that are unique to distributed training.

MPI based
---------

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
-------------

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
----------------

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
---------

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

.. code-block:: console

    az ml job create --file iris-sweep.yml --name <unique name>


Other Job Types
---------------

Coming soon:
- PipelineJob
- AutoMLJob (s)

.. literalinclude:: ../../examples/commandjob.yml
