FROM python:3.10 AS builder

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 复制项目文件
COPY . /app/

# 如果有前端构建步骤，可以在这里添加
# 例如: RUN cd web && npm install && npm run build

# 暴露端口
EXPOSE 3003

# 启动命令
CMD ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "3003", "--workers", "1"]