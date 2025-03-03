set -x

# 基础配置
LR=1e-4
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=glm_4_9b_chat
OUTPUT_DIR=/root/autodl-fs/checkpoint/sft/${RUN_NAME}-${DATESTR}
mkdir -p $OUTPUT_DIR

MODEL_PATH="/root/autodl-fs/modelscope/glm_4_9b_chat"
DATA_PATH="/root/autodl-tmp/EasyDS/data/rlhf_data/sft"


read -r -d '' training_commands <<EOF
openrlhf.cli.train_sft \
    --max_len 200 \
    --dataset json@${DATA_PATH} \
    --input_key input \
    --output_key output \
    --train_batch_size 4 \
    --micro_train_batch_size 1 \
    --max_samples 50000 \
    --pretrain ${MODEL_PATH} \
    --save_path ${OUTPUT_DIR} \
    --save_steps -1 \
    --logging_steps 1 \
    --eval_steps -1 \
    --zero_stage 3 \
    --max_epochs 3 \
    --bf16 \
    --flash_attn \
    --learning_rate ${LR} \
    --lora_rank 4 \
    --lora_alpha 16 \
    --lora_dropout 0.1 \
    --train_split train \
    --eval_split test \
    --apply_chat_template
EOF

if [[ ${1} != "slurm" ]]; then
    deepspeed --module $training_commands
fi