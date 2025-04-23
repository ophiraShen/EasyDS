FROM python:3.10

WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 如果有前端构建步骤，可以在这里添加
# 例如: RUN cd web && npm install && npm run build

# 暴露端口
EXPOSE 3003

# 启动命令
CMD ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "3003", "--workers", "1"]