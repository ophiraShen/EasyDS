#!/bin/bash
vllm serve /root/autodl-fs/modelscope/Qwen2.5-7B-Instruct \
    --served-model-name qwen2.5 \
    --dtype auto \
    --trust-remote-code \
    --host 0.0.0.0 \
    --port 6003 \
    --gpu-memory-utilization 0.7 \
    --max-model-len 4096 \
    --max-num-seqs 128 \
    --tool-call-parser hermes \
    --enable-auto-tool-choice