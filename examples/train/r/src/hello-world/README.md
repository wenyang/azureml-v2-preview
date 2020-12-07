# Hello World Example

This is the obligatory "hello, world!" example.

## Prerequisites
Ensure you have created an environment in Azure ML for running R jobs.

```bash
cd examples/r
az ml environment create --file environment.yaml
```

## Run the job

To run the job use:

```bash
cd examples/r/hello-world
az ml job create --file job.yaml --name $(uuidgen) --stream
