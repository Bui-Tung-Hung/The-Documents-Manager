#!/bin/bash

echo "🚀 Starting Document Search API..."
echo "======================================="

# Install additional API dependencies
echo "📦 Installing API dependencies..."
pip install -r requirements_api.txt

# Check if Qdrant connection works
echo "🔗 Checking Qdrant connection..."
python -c "
try:
    from qdrant_manager import SearchDocument
    import config_docker as config
    searcher = SearchDocument(collection_name='TestCollection6', url=config.url, api_key=config.api_key)
    searcher.init()
    print('✅ Qdrant connection successful')
except Exception as e:
    print(f'❌ Qdrant connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Qdrant connection test failed. Please check your configuration."
    exit 1
fi

# Start the API server
echo "🌟 Starting FastAPI server on http://localhost:8001"
echo "📚 API Documentation available at: http://localhost:8001/docs"
echo "🔍 Health check: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================="

uvicorn app:app --reload --port 8001 --host 0.0.0.0
