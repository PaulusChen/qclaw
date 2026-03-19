# QCLaw Backend Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Configure proxy for PyPI access (Clash proxy)
# Docker network: 10.1.0.0/16, Physical network: 192.168.50.0/24 (direct access)
ENV HTTP_PROXY=http://clash:bH8qpf@192.168.50.106:7890
ENV HTTPS_PROXY=http://clash:bH8qpf@192.168.50.106:7890
ENV NO_PROXY=localhost,127.0.0.1,10.1.0.0/16,192.168.50.0/24,*.paulchen.cn

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY server/requirements.txt .
# Use Tsinghua PyPI mirror for faster downloads in China
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY server/ ./
COPY tests/ ./tests/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command for API service (can be overridden in docker-compose.yml)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
