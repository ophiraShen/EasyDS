#!/bin/bash
set -x

# 设置环境变量以获取更详细的日志
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32
export NCCL_DEBUG=INFO

# 基础配置
DATESTR=`date +%Y%m%d-%H%M%S`
RUN_NAME=qwen2.5_7b_instruct
SAVE_PATH=/root/autodl-fs/checkpoint/ppo/${RUN_NAME}-ppo-${DATESTR}
mkdir -p $SAVE_PATH

# 模型路径配置
PRETRAIN_MODEL_PATH="/root/autodl-fs/modelscope/Qwen2.5-7B-Instruct"  # 或者使用SFT后的模型
REWARD_MODEL_PATH="/root/autodl-fs/checkpoint/rm/qwen2.5_7b_instruct-rm-20250306-021144_lora_combined"  # 使用训练好的RM模型

# 数据路径
PROMPT_DATA_PATH="/root/autodl-tmp/EasyDS/data/rlhf_data/ppo"


read -r -d '' training_commands <<EOF
openrlhf.cli.train_ppo \
   --pretrain ${PRETRAIN_MODEL_PATH} \
   --reward_pretrain ${REWARD_MODEL_PATH} \
   --critic_pretrain ${PRETRAIN_MODEL_PATH} \
   --save_path ${SAVE_PATH} \
   --save_steps -1 \
   --logging_steps 1 \
   --eval_steps -1 \
   --micro_train_batch_size 2 \
   --train_batch_size 4 \
   --micro_rollout_batch_size 2 \
   --rollout_batch_size 4 \
   --max_epochs 1 \
   --prompt_max_len 200 \
   --generate_max_len 200 \
   --zero_stage 3 \
   --bf16 \
   --actor_learning_rate 2e-7 \
   --critic_learning_rate 2e-6 \
   --init_kl_coef 0.01 \
   --prompt_data ${PROMPT_DATA_PATH} \
   --input_key input \
   --apply_chat_template \
   --max_samples 100000 \
   --normalize_reward \
   --adam_offload \
   --flash_attn \
   --load_checkpoint \
   --lora_rank 4 \
   --lora_alpha 16 \
   --lora_dropout 0.05 \
   --target_modules q_proj k_proj v_proj o_proj \
   --overlap_comm
EOF


if [[ ${1} != "slurm" ]]; then
    deepspeed --module $training_commands
fi