set -x

# 基础配置
LR=9e-6
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=glm_4_9b_chat
SAVE_PATH=/root/autodl-fs/checkpoint/rm/${RUN_NAME}-rm-${DATESTR}
mkdir -p $SAVE_PATH

MODEL_PATH="/root/autodl-fs/modelscope/Qwen2.5-7B-Instruct"
DATA_PATH="/root/autodl-tmp/EasyDS/data/rlhf_data/rm"

read -r -d '' training_commands <<EOF
openrlhf.cli.train_rm \
   --save_path ${SAVE_PATH} \
   --save_steps -1 \
   --logging_steps 1 \
   --eval_steps -1 \
   --train_batch_size 4 \
   --micro_train_batch_size 1 \
   --pretrain ${MODEL_PATH} \
   --bf16 \
   --max_epochs 3 \
   --max_len 200 \
   --zero_stage 3 \
   --learning_rate ${LR} \
   --dataset json@${DATA_PATH} \
   --apply_chat_template \
   --chosen_key chosen \
   --rejected_key rejected \
   --flash_attn \
   --load_checkpoint \
   --gradient_checkpointing
EOF
     # --use_wandb [WANDB_TOKENS] or True (use wandb login command)
     # --packing_samples


if [[ ${1} != "slurm" ]]; then
    deepspeed --module $training_commands
fi
