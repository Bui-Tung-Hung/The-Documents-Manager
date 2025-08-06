#!/bin/bash

# Docker entrypoint script for flexible startup
set -e

echo "🚀 Starting Document Search API v2..."

# Check if configuration file is provided
if [ -n "$CONFIG_PATH" ]; then
    echo "📄 Using configuration file: $CONFIG_PATH"
    if [ ! -f "$CONFIG_PATH" ]; then
        echo "❌ Configuration file not found: $CONFIG_PATH"
        exit 1
    fi
fi

# Check required environment variables for cloud deployment
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -z "$QDRANT_URL" ]; then
        echo "❌ QDRANT_URL is required for production environment"
        exit 1
    fi
    
    if [ -z "$QDRANT_API_KEY" ]; then
        echo "⚠️ Warning: QDRANT_API_KEY not set for production"
    fi
fi

# Wait for services if needed
if [ "$WAIT_FOR_SERVICES" = "true" ]; then
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for Qdrant (if using localhost)
    if [[ "$QDRANT_URL" == *"localhost"* ]] || [[ "$QDRANT_URL" == *"127.0.0.1"* ]]; then
        echo "⏳ Waiting for Qdrant..."
        until curl -f http://localhost:6333/collections 2>/dev/null; do
            echo "⏳ Qdrant not ready, waiting..."
            sleep 2
        done
        echo "✅ Qdrant is ready"
    fi
    
    # Wait for Ollama (if using localhost)
    if [[ "$OLLAMA_BASE_URL" == *"localhost"* ]] || [[ "$OLLAMA_BASE_URL" == *"127.0.0.1"* ]]; then
        echo "⏳ Waiting for Ollama..."
        until curl -f http://localhost:11434/api/tags 2>/dev/null; do
            echo "⏳ Ollama not ready, waiting..."
            sleep 2
        done
        echo "✅ Ollama is ready"
    fi
fi

# Run configuration check if requested
if [ "$CHECK_CONFIG" = "true" ]; then
    echo "🔍 Checking configuration..."
    python tools/check_config.py
    if [ $? -ne 0 ]; then
        echo "❌ Configuration check failed"
        exit 1
    fi
    echo "✅ Configuration check passed"
fi

# Start the application
echo "🌟 Starting FastAPI application..."
exec "$@"
