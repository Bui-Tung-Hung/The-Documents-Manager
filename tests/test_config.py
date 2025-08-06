"""
Tests for configuration management
"""

import pytest
import tempfile
import os
from pathlib import Path

from app.core.config import ConfigManager, get_config
from app.core.exceptions import ConfigurationError

def test_config_manager_defaults():
    """Test that default configuration loads correctly"""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    assert config.vector_db.provider == "qdrant"
    assert config.embedding.provider == "ollama"
    assert config.api.port == 8001
    assert config.environment == "development"

def test_config_from_yaml_file():
    """Test loading configuration from YAML file"""
    config_content = """
vector_db:
  provider: "qdrant"
  url: "http://test.com"
  collection: "TestCollection"

embedding:
  provider: "ollama"
  model: "test-model"

api:
  port: 9001
  
environment: "test"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        
        try:
            config_manager = ConfigManager(f.name)
            config = config_manager.load_config()
            
            assert config.vector_db.url == "http://test.com"
            assert config.vector_db.collection == "TestCollection"
            assert config.embedding.model == "test-model"
            assert config.api.port == 9001
            assert config.environment == "test"
        finally:
            os.unlink(f.name)

def test_environment_variable_override():
    """Test that environment variables override config file values"""
    # Set environment variable
    os.environ["QDRANT_URL"] = "http://env-override.com"
    os.environ["API_PORT"] = "8080"
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        assert config.vector_db.url == "http://env-override.com"
        assert config.api.port == 8080
    finally:
        # Clean up
        os.environ.pop("QDRANT_URL", None)
        os.environ.pop("API_PORT", None)
