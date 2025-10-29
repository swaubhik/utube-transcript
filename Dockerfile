# Multi-stage Dockerfile for utube-transcript

# CPU-only variant (lightweight)
FROM python:3.11-slim as cpu

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY pyproject.toml .
COPY README.md .

# Install the package in editable mode
RUN pip install -e .

CMD ["utube-transcript-interactive"]

# GPU variant with CUDA support using PyTorch base image
FROM pytorch/pytorch:2.9.0-cuda12.8-cudnn9-runtime as gpu

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install (PyTorch already included in base image)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY pyproject.toml .
COPY README.md .

# Install the package in editable mode
RUN pip install -e .

CMD ["utube-transcript-interactive"]
