```
az ml dataset create dataset.yml
```

```
az ml compute create gpu-cluster.yml
```

```
az ml job create traintorch.yml

traintorch.yml
inputs:
  mnist: 
   - https://azureopendatastorage.blob.core.windows.net/mnist/train-images-idx3-ubyte.gz
   - https://azureopendatastorage.blob.core.windows.net/mnist/train-labels-idx1-ubyte.gz
   - https://azureopendatastorage.blob.core.windows.net/mnist/t10k-images-idx3-ubyte.gz
   - https://azureopendatastorage.blob.core.windows.net/mnist/t10k-labels-idx1-ubyte.gz
command: >-
    python train.py
    --data { inputs.mnist }
    --epochs 14
    --batch-size 64
    --test-batch-size 1000
    --lr 1.0
    --gamma 0.7
container: docker:pytorch/pytorch
code: ./src
compute: 
  target: cpu-cluster
  node_count: 4
```

// sweep this job //
```
az ml job create sweepjob.yml

type: Sweep
inputs:
  epochs: 14
search_space:
  lr:
    uniform:
      min: 0.001
      max: 0.1
objective:
    primary_metric: accuracy
    goal: maximize     
algorithm: random
trial:
  job: traintorch.yml
  command:  >-
      python train.py
      --data { job.inputs.mnist }
      --epochs { inputs.epochs }
      --batch-size 64
      --test-batch-size 1000
      --lr {search_space.lr}
      --gamma 0.7
```

 // workflow job
```
type: Workflow
 jobs:
   prep:
     command: python prep.py --output-dir {outputs.prepped_data.from}
     code: ./src
     outputs: 
      prepped_data: 
        from: /outputs/prepped_data
   train:
     needs: prep
     command: python train.py --data {needs.prep.outputs.prepped_data}
     code: ./src
     
 // workflow job with a component
 type: Workflow
 jobs:
   prep:
     command: python prep.py --output-dir {outputs.prepped_data.from}
     code: ./src
     outputs: 
      prepped_data: 
        from: /outputs/prepped_data
   train:
     needs: prep
     uses: train_component@main
     with:
      prepped_data: {needs.prep.prepped_data}
```
