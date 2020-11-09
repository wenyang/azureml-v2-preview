(WIP)
```
jobs:
  job:
    data:
      dataset: 
        mount: azureml:/datasets/mnist_data
      model:
        upload: {env.model_dir}
    env:
      model_dir: model 
      lr: 0.09
    runs-on: azureml:/computes/foo_compute
    code: ./src
    steps:
      - run: python train.py --train {inputs.dataset} --model {env.model_dir} --learning_rate {env.lr}
        code: ./other
```
