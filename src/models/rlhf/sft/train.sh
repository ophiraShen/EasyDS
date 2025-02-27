

# 设置环境变量
export CUDA_VISIBLE_DEVICES=0
export TORCH_DISTRIBUTED_DEBUG=INFO
export NCCL_DEBUG=INFO
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_LAUNCH_BLOCKING=1

set -ex

# 基础配置
LR=1e-4
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=easy_ds
OUTPUT_DIR=output/${RUN_NAME}-${DATESTR}
mkdir -p $OUTPUT_DIR

# 模型路径
MODEL_PATH="/root/autodl-fs/modelscope/glm_4_9b_chat"

# DeepSpeed 训练启动命令
accelerate launch \
    --config_file /root/autodl-tmp/EasyDS/scripts/rlhf/default_config.yaml \
    train.py \
    --do_train \
    --do_eval \
    --bf16 \
    --train_file /root/autodl-tmp/EasyDS/data/rlhf_data/sft/train.jsonl \
    --validation_file /root/autodl-tmp/EasyDS/data/rlhf_data/sft/val.jsonl \
    --prompt_column input \
    --response_column output \
    --max_source_length 200 \
    --max_target_length 150 \
    --model_name_or_path "${MODEL_PATH}" \
    --output_dir $OUTPUT_DIR \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 4 \
    --gradient_accumulation_steps 16 \
    --learning_rate $LR \
    --num_train_epochs 3\
    --weight_decay 0.01 \
    --warmup_ratio 0.1 \
    --lora_rank 4 \
    --lora_alpha 16 \
    --lora_dropout 0.1 \
    --target_modules "query_key_value" \
    --save_strategy "steps" \
    --save_steps 30 \
    --save_total_limit 3 \
    --eval_strategy steps \
    --eval_steps 20 \
    --logging_dir $OUTPUT_DIR/runs \
    --logging_strategy steps \
    --logging_steps 10 \
    --report_to tensorboard \
    2>&1 | tee ${OUTPUT_DIR}/train.log