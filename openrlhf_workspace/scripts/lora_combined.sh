set -x

MODEL_PATH="/root/autodl-fs/modelscope/Qwen2.5-7B-Instruct"
LORA_PATH="/root/autodl-fs/checkpoint/rm/qwen2.5_7b_instruct-rm-20250306-021144"
OUTPUT_PATH=${LORA_PATH}_lora_combined

python -m openrlhf.cli.lora_combiner \
    --model_path ${MODEL_PATH} \
    --lora_path ${LORA_PATH} \
    --output_path ${OUTPUT_PATH} \
    --is_rm \
    --bf16