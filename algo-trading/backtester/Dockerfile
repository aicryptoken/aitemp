FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Download and install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    # Update config.guess and config.sub for aarch64 support
    wget -O config.guess 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD' && \
    wget -O config.sub 'http://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD' && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

# Set environment variables for TA-Lib
ENV TA_INCLUDE_PATH=/usr/include
ENV TA_LIBRARY_PATH=/usr/lib

# Install TA-Lib Python wrapper
RUN pip install --no-cache-dir ta-lib

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/data /app/strategies /app/backtester

# Set Python path
ENV PYTHONPATH=/app

# Mount volumes
VOLUME ["/app/data", "/app/strategies", "/app/backtester"]

# Keep container running
CMD ["/bin/bash"]