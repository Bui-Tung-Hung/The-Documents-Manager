# Makefile for Document Search API v2

.PHONY: help install dev test lint format clean docker docker-local run health check-config

# Default target
help:
	@echo "🔍 Document Search API v2 - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install          Install dependencies"
	@echo "  dev             Install development dependencies"
	@echo ""
	@echo "🚀 Development:"
	@echo "  run             Run the API server"
	@echo "  run-dev         Run with development config"
	@echo "  run-prod        Run with production config"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  test            Run all tests"
	@echo "  test-coverage   Run tests with coverage"
	@echo "  lint            Run linting"
	@echo "  format          Format code"
	@echo "  check-config    Validate configuration"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker          Build and run with Docker"
	@echo "  docker-local    Run with local services"
	@echo "  docker-build    Build Docker image"
	@echo ""
	@echo "🔧 Utilities:"
	@echo "  health          Check API health"
	@echo "  clean           Clean up temporary files"
	@echo "  upload-s3       Upload sample documents to S3"
	@echo "  send-sqs        Send sample messages to SQS"
	@echo "  process-queue   Process SQS messages"

# Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

dev:
	@echo "🛠️ Installing development dependencies..."
	pip install -r requirements.txt pytest pytest-asyncio black flake8 mypy

# Development
run:
	@echo "🚀 Starting API server..."
	python -m app.main

run-dev:
	@echo "🚀 Starting API server with development config..."
	CONFIG_PATH=config/config.dev.yaml python -m app.main

run-prod:
	@echo "🚀 Starting API server with production config..."
	CONFIG_PATH=config/config.prod.yaml python -m app.main

# Testing & Quality
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:
	@echo "🔍 Running linting..."
	flake8 app/ tools/ scripts/ tests/
	mypy app/ tools/

format:
	@echo "✨ Formatting code..."
	black app/ tools/ scripts/ tests/

check-config:
	@echo "🔍 Checking configuration..."
	python tools/check_config.py

# Docker
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -f docker/Dockerfile -t document-search-api:v2 .

docker:
	@echo "🐳 Building and running with Docker..."
	docker-compose up --build

docker-local:
	@echo "🐳 Running with local services..."
	docker-compose --profile local up -d

# Utilities
health:
	@echo "🏥 Checking API health..."
	curl -f http://localhost:8001/health | python -m json.tool

clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

# AWS Simulation Scripts
upload-s3:
	@echo "📤 Uploading sample documents to S3..."
	python scripts/upload_to_s3.py

send-sqs:
	@echo "📨 Sending sample messages to SQS..."
	python scripts/send.py

process-queue:
	@echo "📥 Processing SQS messages..."
	python scripts/receive.py

# Environment setup
setup-env:
	@echo "⚙️ Setting up environment..."
	cp .env.example .env
	@echo "✅ Environment file created. Please edit .env with your configuration."

# Complete setup for new developers
setup: setup-env install check-config
	@echo "🎉 Setup complete! You can now run 'make run' to start the API."
