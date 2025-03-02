set -x

# 基础配置
LR=1e-4
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=easy_ds
OUTPUT_DIR=/root/autodl-tmp/EasyDS/openrlhf_workspace/outputs/sft/${RUN_NAME}-${DATESTR}
mkdir -p $OUTPUT_DIR

MODEL_PATH="/root/autodl-fs/modelscope/glm_4_9b_chat"
DATA_PATH="/root/autodl-tmp/EasyDS/data/rlhf_data/sft"


read -r -d '' training_commands <<EOF
openrlhf.cli.train_sft \
    --max_len 200 \
    --dataset jsonl@${DATA_PATH} \
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
    --gradient_checkpointing \
    --flash_attn \
    --learning_rate ${LR} \
    --lora_rank 4 \
    --lora_alpha 16 \
    --lora_dropout 0.1 \
    --aux_loss_coef 0.001
EOF

if [[ ${1} != "slurm" ]]; then
    deepspeed --module $training_commands
fi