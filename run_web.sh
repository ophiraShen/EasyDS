#!/bin/bash

echo "=== 安装依赖 ==="
# pip install -r ./web/requirements.txt

echo "=== 启动服务器 ==="
# cd autodl-tmp/EasyDS

# 在生产环境中，不建议使用 --reload 参数
# 这可能会导致流式响应问题
# 改为使用workers提高性能和稳定性
python -m uvicorn web.main:app --host 0.0.0.0 --port 8008 --workers 1