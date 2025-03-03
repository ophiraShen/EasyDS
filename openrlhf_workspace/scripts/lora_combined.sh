set -x

MODEL_PATH="/root/autodl-fs/modelscope/glm_4_9b_chat"
LORA_PATH="/root/autodl-fs/checkpoint/sft/glm_4_9b_chat-20250303-024747"
OUTPUT_PATH=${LORA_PATH}_lora_combined

python -m openrlhf.cli.lora_combiner \
    --model_path ${MODEL_PATH} \
    --lora_path ${LORA_PATH} \
    --output_path ${OUTPUT_PATH} \
    --is_rm \
    --bf16