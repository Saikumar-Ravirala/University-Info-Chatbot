# Use Python 3.11 slim for smaller base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for all ML packages
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for memory optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy ALL backend files from current directory (backend/) to /app in container
COPY . .

# Create necessary directories
RUN mkdir -p logs 

# Expose port
EXPOSE 8000

# Set memory limits and start with single worker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "30"]