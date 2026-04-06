# 多阶段构建 - 后端 API 服务
FROM python:3.11-slim as base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 启动命令
CMD ["python", "main.py"]

# 开发环境阶段
FROM base as development
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
CMD ["python", "main.py"]

# 生产环境阶段
FROM base as production
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
