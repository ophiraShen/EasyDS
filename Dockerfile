FROM python:3.11-slim

# 创建工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=100 -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露端口
EXPOSE 3003

# 启动命令
CMD ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "3003", "--workers", "1"]