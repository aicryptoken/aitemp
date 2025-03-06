FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY tests/ ./tests/

# 设置环境变量
ENV STRATEGIES_DIR=/strategies

# 创建策略目录的挂载点
RUN mkdir -p $STRATEGIES_DIR

CMD ["python", "-m", "unittest", "discover", "tests"]