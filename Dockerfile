# 打卡树后端镜像（FastAPI + 静态前端）
FROM python:3.12-slim

# 不生成 .pyc、日志实时输出、时区数据
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# curl 供健康检查使用
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖（利用 Docker 层缓存：requirements 不变就不重装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再拷贝源码
COPY . .

# 数据库/数据卷的挂载点
RUN mkdir -p /app/data
ENV DB_FILE=/app/data/database.db

EXPOSE 8000

# 默认以单进程方式启动（各环境会用 compose 的 command 覆盖）
CMD ["python", "main.py"]
