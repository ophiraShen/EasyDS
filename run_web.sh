#!/bin/bash

echo "=== 启动服务器 ==="
# cd autodl-tmp/EasyDS

python -m uvicorn web.main:app --host 0.0.0.0 --port 3003 --workers 1