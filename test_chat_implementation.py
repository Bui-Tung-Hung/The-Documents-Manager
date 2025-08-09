#!/usr/bin/env python3
"""
Test script để validate chat implementation
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_loading():
    """Test config loading với chat section"""
    try:
        from app.core.config import get_config
        config = get_config()
        
        print("✅ Config loaded successfully")
        print(f"Chat provider: {config.chat.provider}")
        print(f"Chat model: {config.chat.model}")
        print(f"Chat base URL: {config.chat.base_url}")
        print(f"Context limit: {config.chat.context_limit}")
        print(f"Max chunks: {config.chat.max_chunks}")
        
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_imports():
    """Test all imports resolve correctly"""
    try:
        from app.api.models import ChatWithFilesRequest, ChatWithFilesResponse
        from app.services.chat_service import ChatService
        from app.providers.chat.ollama import OllamaChatProvider
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_api_models():
    """Test API models validation"""
    try:
        from app.api.models import ChatWithFilesRequest
        
        # Test valid request
        request = ChatWithFilesRequest(
            file_ids=["doc_001", "doc_002"],
            message="Test message",
            max_chunks=3
        )
        print("✅ API models validation successful")
        print(f"Request: {request}")
        
        return True
    except Exception as e:
        print(f"❌ API models test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing chat implementation...")
    
    all_passed = True
    
    print("\n1. Testing config loading...")
    all_passed &= test_config_loading()
    
    print("\n2. Testing imports...")
    all_passed &= test_imports()
    
    print("\n3. Testing API models...")
    all_passed &= test_api_models()
    
    if all_passed:
        print("\n🎉 All tests passed! Chat implementation is ready.")
    else:
        print("\n❌ Some tests failed. Check implementation.")
        sys.exit(1)
