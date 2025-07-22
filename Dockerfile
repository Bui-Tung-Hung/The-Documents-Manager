# Multi-stage Dockerfile for All-in-One Document Search API Container
# Includes: FastAPI + Qdrant + Ollama + BGE-M3 Model

FROM ubuntu:22.04 AS base

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Stage 2: Install Ollama
FROM base as ollama-stage

# Download and install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Pre-download BGE-M3 model
RUN ollama serve & \
    until curl -s http://localhost:11434 > /dev/null; do echo "Waiting for Ollama..."; sleep 1; done && \
    ollama pull bge-m3:latest


# Stage 3: Install Python dependencies and API
FROM ollama-stage as final

# Copy and install Python requirements
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make entrypoint executable
RUN chmod +x start_api.sh

# Create directories for logs and data
RUN mkdir -p /var/log/supervisor /app/data /app/scripts

# Expose API port
EXPOSE 8001

# Set entrypoint
ENTRYPOINT ["./start_api.sh"]