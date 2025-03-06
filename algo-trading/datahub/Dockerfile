FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY src/ ./src/

# 创建数据目录
RUN mkdir -p /app/data

# 设置 Python 路径
ENV PYTHONPATH=/app

VOLUME ["/app/data"]

CMD ["/bin/bash"]

# In future, change to autorun
# CMD ["python", "main.py"]