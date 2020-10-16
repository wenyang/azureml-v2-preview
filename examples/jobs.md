// run a job
```
command: >-
    python train.py
    --data { mount: dataset_id_or_name }
    --epochs 14
    --batch-size 64
    --test-batch-size 1000
    --lr 1.0
    --gamma 0.7
    --save_model { upload: outputs/model_dir }
environment: docker:pytorch/pytorch
code: ./src
compute: 
  target: cpu-cluster
  node_count: 4
```

// sweep this job //
```
type: Sweep
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
  job_id: my_job_id // reuses values from job, only things specified are overridden
  command:  >-
      python train.py
      --data { mount: /to/my/data }
      --epochs 14
      --batch-size 64
      --test-batch-size 1000
      --lr {search_space.lr}
      --gamma 0.7
      --save_model { upload: outputs/model_dir }
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
