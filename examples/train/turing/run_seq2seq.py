from __future__ import absolute_import, division, print_function

import argparse
import logging
import os
import json
import random
import shutil
import hashlib

import numpy as np
import torch
from torch.utils.data import DataLoader, SequentialSampler
from torch.utils.data.distributed import DistributedSampler

from basic_logging import Basic

import tqdm

from tnlr.modeling import (
    TuringNLRv3ForSequenceToSequenceWithPseudoMask,
    TuringNLRv3ForSequenceToSequenceUniLMV1,
)
from transformers import AdamW, get_linear_schedule_with_warmup
from tnlr.configuration_tnlrv3 import TuringNLRv3Config
from tnlr.tokenization_tnlrv3 import TuringNLRv3Tokenizer

from tnlr import utils
from tnlr.config import TuringNLRv3ForSeq2SeqConfig

from azureml_adapter import *

from azureml.core import Run
from basic_logging import is_main_process

from onnxruntime.training import orttrainer, optim, amp
from onnxruntime.training.orttrainer import ORTTrainer, ORTTrainerOptions
from onnxruntime.training.checkpoint import (
    experimental_state_dict,
    experimental_load_state_dict,
)

logger = logging.getLogger(__name__)
run = Run.get_context()

MODEL_CLASSES = {
    "tnlrv3": (TuringNLRv3Config, TuringNLRv3Tokenizer),
}


def save_ort_checkpoint(model, args, step):
    path = args.output_dir
    upload_path = args.upload_dir
    if args.rank == 0:
        logger.info("Saving model checkpoint %d into %s", step, path)
        os.makedirs(path, exist_ok=True)
        save_path = os.path.join(path, "ckpt-%d" % step)
        torch.save(experimental_state_dict(model), save_path)

        with open(os.path.join(path, "step.txt"), "w") as f:
            f.write(str(step))

        logger.info("Uploading model checkpoint %d into %s", step, path)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        upload_file_name = os.path.join(upload_path, "ckpt-%d" % step)
        try:
            shutil.copyfile(save_path, upload_file_name)
        except Exception as e:
            print(f"Fail to copy checkpoint to cloud mount. ({e})")

    logger.info("Completed saving and uploading checkpoint")
    return


def train(args, training_features, model, tokenizer):
    stats = Basic(args)
    logger.info(f"created stats instance: {stats}")
    stats.build_writers(run)

    currRunId = run.get_details()["runId"]

    """ Train the model """
    # model recover
    recover_step = utils.get_max_epoch_model(args.output_dir)
    logger.info(f"Restart training from {recover_step}")
    if recover_step:
        checkpoint_state_dict = utils.get_checkpoint_state_dict(
            args.output_dir, recover_step
        )
    else:
        checkpoint_state_dict = None

    model.to(args.device)

    per_node_train_batch_size = (
        args.per_gpu_train_batch_size * args.n_gpu * args.gradient_accumulation_steps
    )
    train_batch_size = per_node_train_batch_size * (
        torch.distributed.get_world_size() if args.local_rank != -1 else 1
    )
    global_step = recover_step if recover_step else 0
    num_training_samples = len(training_features)

    if args.num_training_steps == -1:
        args.num_training_steps = (
            args.num_training_epochs * len(training_features) // train_batch_size
        )

    model_desc = {
        "inputs": [
            ("source_ids", [args.per_gpu_train_batch_size, args.max_source_seq_length]),
            ("target_ids", [args.per_gpu_train_batch_size, args.max_target_seq_length]),
            ("label_ids", [args.per_gpu_train_batch_size, args.max_target_seq_length]),
            ("pseudo_ids", [args.per_gpu_train_batch_size, args.max_target_seq_length]),
            ("num_source_tokens", [args.per_gpu_train_batch_size]),
            ("num_target_tokens", [args.per_gpu_train_batch_size]),
        ],
        "outputs": [("loss", [], True)],
    }

    param_optimizer = list(model.named_parameters())
    no_decay = ["bias", "LayerNorm"]
    optim_config = optim.AdamConfig(
        params=[
            {
                "params": [
                    n for n, p in param_optimizer if any(nd in n for nd in no_decay)
                ],
                "lambda_coef": 0.0,
            }
        ],
        lr=args.learning_rate,
        alpha=0.9,
        beta=0.999,
        lambda_coef=args.weight_decay,
        epsilon=args.adam_epsilon,
    )

    warmup = args.num_warmup_steps / args.num_training_steps
    lr_scheduler = optim.lr_scheduler.LinearWarmupLRScheduler(
        total_steps=args.num_training_steps, warmup=warmup
    )

    loss_scaler = (
        amp.DynamicLossScaler(automatic_update=True, up_scale_window=2000)
        if args.fp16
        else None
    )

    opts = orttrainer.ORTTrainerOptions(
        {
            "device": {"id": str(args.device)},
            "distributed": {
                "world_rank": args.rank,
                "world_size": args.global_size,
                "local_rank": args.local_rank,
                "allreduce_post_accumulation": True,
            },
            "mixed_precision": {"enabled": args.fp16, "loss_scaler": loss_scaler},
            "batch": {"gradient_accumulation_steps": args.gradient_accumulation_steps},
            "lr_scheduler": lr_scheduler,
        }
    )

    model = orttrainer.ORTTrainer(model, model_desc, optim_config, None, options=opts)

    train_dataset = utils.Seq2seqDatasetForTuringNLRv3(
        features=training_features,
        max_source_len=args.max_source_seq_length,
        max_target_len=args.max_target_seq_length,
        vocab_size=tokenizer.vocab_size,
        cls_id=tokenizer.cls_token_id,
        sep_id=tokenizer.sep_token_id,
        pad_id=tokenizer.pad_token_id,
        mask_id=tokenizer.mask_token_id,
        random_prob=args.random_prob,
        keep_prob=args.keep_prob,
        offset=train_batch_size * global_step,
        num_training_instances=train_batch_size * args.num_training_steps,
        source_mask_prob=args.source_mask_prob,
        target_mask_prob=args.target_mask_prob,
        finetuning_method=args.finetuning_method,
        num_max_mask_token=args.num_max_mask_token,
    )

    logger.info("Check dataset:")
    for i in range(5):
        source_ids, target_ids = train_dataset.__getitem__(i)[:2]
        logger.info("Instance-%d" % i)
        logger.info(
            "Source tokens = %s" % " ".join(tokenizer.convert_ids_to_tokens(source_ids))
        )
        logger.info(
            "Target tokens = %s" % " ".join(tokenizer.convert_ids_to_tokens(target_ids))
        )

    logger.info("Mode = %s" % str(model))

    # Train!
    logger.info("  ***** Running training *****  *")
    logger.info("  Num examples = %d", len(training_features))
    # logger.info("  Num Augmented examples = %d", len(train_dataset) )
    logger.info("  Num Epochs = %.2f", len(train_dataset) / len(training_features))
    logger.info(
        "  Instantaneous batch size per GPU = %d", args.per_gpu_train_batch_size
    )
    logger.info("  Batch size per node = %d", per_node_train_batch_size)
    logger.info(
        "  Total train batch size (w. parallel, distributed & accumulation) = %d",
        train_batch_size,
    )
    logger.info("  Gradient Accumulation steps = %d", args.gradient_accumulation_steps)
    logger.info("  Total optimization steps = %d", args.num_training_steps)

    if args.num_training_steps <= global_step:
        logger.info("Training is done. Please use a new dir or clean this dir!")
    else:
        # The training features are shuffled
        train_sampler = (
            SequentialSampler(train_dataset)
            if args.local_rank == -1
            else DistributedSampler(train_dataset, shuffle=False)
        )
        train_dataloader = DataLoader(
            train_dataset,
            sampler=train_sampler,
            batch_size=per_node_train_batch_size // args.gradient_accumulation_steps,
            collate_fn=utils.batch_list_to_batch_tensors,
        )

        train_iterator = tqdm.tqdm(
            train_dataloader,
            initial=global_step * args.gradient_accumulation_steps,
            desc="Iter (loss=X.XXX, lr=X.XXXXXXX)",
            disable=args.rank not in [-1, 0],
            miniters=20,
            mininterval=10,
            maxinterval=60,
        )  # less frequent update of progress bar

        tr_loss, logging_loss = 0.0, 0.0

        for step, batch in enumerate(train_iterator):
            if global_step > args.num_training_steps:
                break
            batch = tuple(t.to(args.device) for t in batch)
            if args.finetuning_method == "v2":
                inputs = {
                    "source_ids": batch[0],
                    "target_ids": batch[1],
                    "label_ids": batch[2],
                    "pseudo_ids": batch[3],
                    "num_source_tokens": batch[4],
                    "num_target_tokens": batch[5],
                }
            elif args.finetuning_method == "v1" or args.finetuning_method == "v0":
                inputs = {
                    "source_ids": batch[0],
                    "target_ids": batch[1],
                    "masked_ids": batch[2],
                    "masked_pos": batch[3],
                    "masked_weight": batch[4],
                    "num_source_tokens": batch[5],
                    "num_target_tokens": batch[6],
                }

            loss = model.train_step(
                batch[0], batch[1], batch[2], batch[3], batch[4], batch[5]
            )
            lr_step = lr_scheduler.get_last_lr()[0]

            if args.n_gpu > 1:
                loss = (
                    loss.mean()
                )  # mean() to average on multi-gpu parallel (not distributed) training

            if (
                step % 20 == 0
            ) and args.rank == 0:  # update desc every 10 steps and log to AML
                train_iterator.set_description(
                    "Iter (loss=%5.3f) lr=%9.7f" % (loss.item(), lr_step)
                )

            if is_main_process(args):
                stats.update(
                    "trainer/training_loss", np.float(loss.item()), frequent=True
                )
                stats.update("trainer/steps", step + 1, frequent=True)
                stats.update(
                    "trainer/learning_rate", np.float(lr_step), frequent=True,
                )
                stats.log_short_stats(step, delay=2)

            if args.gradient_accumulation_steps > 1:
                loss = loss / args.gradient_accumulation_steps

            logging_loss += loss.item()
            if (step + 1) % args.gradient_accumulation_steps == 0:
                global_step += 1

                if (
                    args.local_rank in [-1, 0]
                    and args.logging_steps > 0
                    and global_step % args.logging_steps == 0
                ):
                    logger.info("")
                    logger.info(
                        " Step [%d ~ %d]: %.2f",
                        global_step - args.logging_steps,
                        global_step,
                        logging_loss,
                    )
                    logging_loss = 0.0

                if (
                    is_main_process(args)
                    and args.save_steps > 0
                    and (
                        global_step % args.save_steps == 0
                        or global_step == args.num_training_steps
                    )
                ):
                    save_ort_checkpoint(model, args, global_step)

    stats.finish()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train_file",
        default=None,
        type=str,
        required=True,
        help="Training data (json format) for training. Keys: source and target",
    )
    parser.add_argument(
        "--model_type",
        default="tnlrv3",
        type=str,
        help="Model type selected in the list: " + ", ".join(MODEL_CLASSES.keys()),
    )
    parser.add_argument(
        "--model_name_or_path",
        default=None,
        type=str,
        required=True,
        help="Path to pre-trained model or shortcut name selected in the list:",
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        type=str,
        required=True,
        help="The output directory where the model checkpoints and predictions will be written.",
    )
    parser.add_argument(
        "--upload_dir",
        default=None,
        type=str,
        required=True,
        help="The direcotry that will be uploaded to cloud storage.",
    )
    parser.add_argument(
        "--log_dir",
        default="logs",
        type=str,
        help="The output directory where the log will be written.",
    )
    parser.add_argument(
        "--upload_cache",
        action="store_true",
        help="Set this flag if want to upload feature cache to cloud storage",
    )
    ## Other parameters
    parser.add_argument(
        "--config_name",
        default=None,
        type=str,
        help="Pretrained config name or path if not the same as model_name",
    )
    parser.add_argument(
        "--tokenizer_name",
        default=None,
        type=str,
        help="Pretrained tokenizer name or path if not the same as model_name",
    )
    parser.add_argument(
        "--cache_dir",
        default=None,
        type=str,
        help="Where do you want to store the pre-trained models downloaded from s3",
    )

    parser.add_argument(
        "--max_source_seq_length",
        default=464,
        type=int,
        help="The maximum total source sequence length after WordPiece tokenization. Sequences "
        "longer than this will be truncated, and sequences shorter than this will be padded.",
    )
    parser.add_argument(
        "--max_target_seq_length",
        default=48,
        type=int,
        help="The maximum total target sequence length after WordPiece tokenization. Sequences "
        "longer than this will be truncated, and sequences shorter than this will be padded.",
    )

    parser.add_argument(
        "--cached_train_features_file",
        default=None,
        type=str,
        help="Cached training features file",
    )
    parser.add_argument(
        "--do_lower_case",
        action="store_true",
        help="Set this flag if you are using an uncased model.",
    )

    parser.add_argument(
        "--per_gpu_train_batch_size",
        default=8,
        type=int,
        help="Batch size per GPU/CPU for training.",
    )
    parser.add_argument(
        "--learning_rate",
        default=5e-5,
        type=float,
        help="The initial learning rate for Adam.",
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=1,
        help="Number of updates steps to accumulate before performing a backward/update pass.",
    )
    parser.add_argument(
        "--weight_decay",
        default=0.01,
        type=float,
        help="Weight decay if we apply some.",
    )
    parser.add_argument(
        "--adam_epsilon", default=1e-8, type=float, help="Epsilon for Adam optimizer."
    )
    parser.add_argument(
        "--max_grad_norm", default=1.0, type=float, help="Max gradient norm."
    )
    parser.add_argument(
        "--label_smoothing", default=0.1, type=float, help="Max gradient norm."
    )
    parser.add_argument(
        "--num_training_steps",
        default=-1,
        type=int,
        help="set total number of training steps to perform",
    )
    parser.add_argument(
        "--num_training_epochs",
        default=10,
        type=int,
        help="set total number of training epochs to perform (--num_training_steps has higher priority)",
    )
    parser.add_argument(
        "--num_warmup_steps",
        default=0,
        type=int,
        help="Linear warmup over warmup_steps.",
    )

    parser.add_argument(
        "--random_prob",
        default=0.1,
        type=float,
        help="prob to random replace a masked token",
    )
    parser.add_argument(
        "--keep_prob",
        default=0.1,
        type=float,
        help="prob to keep no change for a masked token",
    )
    parser.add_argument(
        "--fix_word_embedding",
        action="store_true",
        help="Set word embedding no grad when finetuning.",
    )

    parser.add_argument(
        "--logging_steps", type=int, default=500, help="Log every X updates steps."
    )
    parser.add_argument(
        "--save_steps",
        type=int,
        default=1500,
        help="Save checkpoint every X updates steps.",
    )
    parser.add_argument(
        "--no_cuda", action="store_true", help="Whether not to use CUDA when available"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="random seed for initialization"
    )

    parser.add_argument(
        "--local_rank",
        type=int,
        default=-1,
        help="local_rank for distributed training on gpus",
    )
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Whether to use 16-bit (mixed) precision (through NVIDIA apex) instead of 32-bit",
    )
    parser.add_argument(
        "--fp16_opt_level",
        type=str,
        default="O1",
        help="For fp16: Apex AMP optimization level selected in ['O0', 'O1', 'O2', and 'O3']."
        "See details at https://nvidia.github.io/apex/amp.html",
    )
    parser.add_argument(
        "--server_ip", type=str, default="", help="Can be used for distant debugging."
    )
    parser.add_argument(
        "--server_port", type=str, default="", help="Can be used for distant debugging."
    )

    parser.add_argument(
        "--source_mask_prob",
        type=float,
        default=-1.0,
        help="Probability to mask source sequence in fine-tuning",
    )
    parser.add_argument(
        "--target_mask_prob",
        type=float,
        default=-1.0,
        help="Probability to mask target sequence in fine-tuning",
    )
    parser.add_argument(
        "--num_max_mask_token",
        type=int,
        default=0,
        help="The number of the max masked tokens in target sequence",
    )
    parser.add_argument(
        "--finetuning_method",
        type=str,
        default="v2",
        help="Fine-tuning method (v0: position shift, v1: masked LM, v2: pseudo-masking)",
    )
    parser.add_argument(
        "--lmdb_cache", action="store_true", help="Use LMDB to cache training features"
    )
    parser.add_argument(
        "--lmdb_dtype",
        type=str,
        default="h",
        help="Data type for cached data type for LMDB",
    )

    parser.add_argument(
        "--writers",
        default="tensorboard-aml",
        type=str,
        help="writers to use for logging stats",
    )
    parser.add_argument(
        "--log_short_steps", default=50, type=int, help="logging short step intervals"
    )
    parser.add_argument(
        "--log_long_steps", default=4000, type=int, help="logging long step intervals"
    )
    parser.add_argument(
        "--tb_logpath_parent_env", default=None, type=str
    )  # AZ_BATCHAI_BLOB_STREAM_CACHE_DIR for compliant aml
    args = parser.parse_args()
    return args


def prepare(args):
    # Setup distant debugging if needed
    if args.server_ip and args.server_port:
        # Distant debugging - see https://code.visualstudio.com/docs/python/debugging#_attach-to-a-local-script
        import ptvsd

        print("Waiting for debugger attach")
        ptvsd.enable_attach(
            address=(args.server_ip, args.server_port), redirect_output=True
        )
        ptvsd.wait_for_attach()

    os.makedirs(args.output_dir, exist_ok=True)
    json.dump(
        args.__dict__,
        open(os.path.join(args.output_dir, "train_opt.json"), "w"),
        sort_keys=True,
        indent=2,
    )

    # Setup CUDA, GPU & distributed training
    if args.local_rank == -1 or args.no_cuda:
        device = torch.device(
            "cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu"
        )
        args.n_gpu = torch.cuda.device_count()
    else:  # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
        torch.cuda.set_device(args.local_rank)
        device = torch.device("cuda", args.local_rank)
        torch.distributed.init_process_group(backend="nccl")
        args.n_gpu = 1
    args.device = device

    from onnxruntime.capi._pybind_state import (
        set_cuda_mem_limit,
        set_arena_extend_strategy,
        ArenaExtendStrategy,
    )

    set_cuda_mem_limit(
        int(torch.cuda.get_device_properties(args.local_rank).total_memory)
    )
    set_arena_extend_strategy(ArenaExtendStrategy.kSameAsRequested)
    from onnxruntime.capi._pybind_state import set_cuda_device_id

    set_cuda_device_id(args.local_rank)

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO if args.local_rank in [-1, 0] else logging.WARN,
    )
    logger.warning(
        "Process rank: %s, device: %s, n_gpu: %s, distributed training: %s, 16-bits training: %s",
        args.local_rank,
        device,
        args.n_gpu,
        bool(args.local_rank != -1),
        args.fp16,
    )

    # Set seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    from onnxruntime import set_seed

    set_seed(args.seed + args.rank)

    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)

    logger.info("Training/evaluation parameters %s", args)


def get_model_and_tokenizer(args):
    config_class, tokenizer_class = MODEL_CLASSES[args.model_type]
    model_config = config_class.from_pretrained(
        args.config_name if args.config_name else args.model_name_or_path,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )
    config = TuringNLRv3ForSeq2SeqConfig.from_exist_config(
        config=model_config,
        label_smoothing=args.label_smoothing,
        fix_word_embedding=args.fix_word_embedding,
        max_position_embeddings=args.max_source_seq_length + args.max_target_seq_length,
    )

    logger.info("Model config for seq2seq: %s", str(config))

    tokenizer = tokenizer_class.from_pretrained(
        args.tokenizer_name if args.tokenizer_name else args.model_name_or_path,
        do_lower_case=args.do_lower_case,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )

    model_class = (
        TuringNLRv3ForSequenceToSequenceWithPseudoMask
        if args.finetuning_method == "v2"
        else TuringNLRv3ForSequenceToSequenceUniLMV1
    )

    logger.info("Construct model %s" % model_class.MODEL_NAME)

    model = model_class.from_pretrained(
        args.model_name_or_path,
        config=config,
        model_type=args.model_type,
        reuse_position_embedding=True,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )

    total_params = 0
    for p in model.parameters():
        total_params += p.numel()
    logger.info(f"Total Model Parameters: {total_params}")

    return model, tokenizer


def main():
    args = get_args()
    # use aml adapter to get local rank from env variable instead of using the argument
    # SET ENV FOR NCCL
    args.local_rank = get_local_rank()
    args.rank = get_rank()
    global_size = get_global_size()
    local_size = get_local_size()
    print("Save outputs to {}".format(args.output_dir))
    print("local_rank = {}".format(args.local_rank))
    print("global_rank = {}".format(args.rank))
    print("global_size = {}".format(global_size))
    print("local_size = {}".format(local_size))
    print("feature cache file = {}".format(args.cached_train_features_file))
    set_environment_variables_for_nccl_backend(local_size == global_size)

    setattr(args, "global_size", global_size)

    prepare(args)

    if args.local_rank not in [-1, 0]:
        torch.distributed.barrier()
        # Make sure only the first process in distributed training will download model & vocab
    # Load pretrained model and tokenizer
    model, tokenizer = get_model_and_tokenizer(args)

    if args.local_rank == 0:
        torch.distributed.barrier()
        # Make sure only the first process in distributed training will download model & vocab

    if args.cached_train_features_file is None:
        if not args.lmdb_cache:
            args.cached_train_features_file = os.path.join(
                args.output_dir, "cached_features_for_training.pt"
            )
        else:
            args.cached_train_features_file = os.path.join(
                args.output_dir, "cached_features_for_training_lmdb"
            )
    training_features = utils.load_and_cache_examples(
        example_file=args.train_file,
        tokenizer=tokenizer,
        local_rank=args.local_rank,
        cached_features_file=args.cached_train_features_file,
        shuffle=True,
        lmdb_cache=args.lmdb_cache,
        lmdb_dtype=args.lmdb_dtype,
    )
    # only head node will save cache to mount
    if args.rank in [-1, 0] and args.upload_cache:
        cached_train_features_file_upload = os.path.join(
            args.upload_dir, "cached_features_for_training.pt"
        )
        os.makedirs(os.path.dirname(cached_train_features_file_upload), exist_ok=True)
        print(
            f"copy feature cache from from {args.cached_train_features_file} to {cached_train_features_file_upload}"
        )
        shutil.copy(args.cached_train_features_file, cached_train_features_file_upload)

    train(args, training_features, model, tokenizer)


if __name__ == "__main__":
    main()
