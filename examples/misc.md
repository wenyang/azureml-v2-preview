```yml
command: ^^^
python aml/train.py
                        --input_dir bert.mt/
                        --job_dir **hash of the command**
                        --do_train
                        --save_best
                        --adls_input {inputs.mrc_dr}
                        --checkpoints_dir' checkpoints/
                        --output_dir {inputs.output_dr}
                        --logs_dir logs/
                        --tasks spanbert.query
                         --max_seq_length 16
                         --do_lower_case False
                         --xlmroberta_model xlm-roberta-large
                         --batch_size 128
                         --learning_rate 1e-5
                         --num_training_epochs 10
                         --num_early_stopping_epochs 1
                         --no_cache
                         --fp16
                         --fp16_opt_level O2
                         --warmup_proportion 0.1
                         --gradient_accumulation_steps 1
                         --reduce_memory
                         --node_count $NODE_COUNT
                         --gpus $GPU_PER_NODE_COUNT
                         --node_rank $NODE_RANK

environment:
  docker:
    image: azureml/deepspeed-2.0

compute:
  type: aisupercomputer
  instance_type: AISupercomputer.ND40rs_v2
  location: westus2
  instance_count: 1

inputs:
  mrc: 
    path: ...
    mode: mount (only)
  output:
    path: ...
```
