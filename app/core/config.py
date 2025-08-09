"""
Configuration manager with multi-source support.
Supports loading from environment variables, .env files, and YAML/JSON config files.
Priority: environment variables > config file > defaults
"""

import os
import yaml
import json
from typing import Optional, Dict, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

@dataclass
class VectorDBConfig:
    """Vector database configuration"""
    provider: str = "qdrant"
    url: str = ""
    api_key: str = ""
    collection: str = "TestCollection6"
    timeout: int = 30

@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    provider: str = "ollama"
    model: str = "bge-m3"
    base_url: str = "http://localhost:11434"
    api_key: str = ""
    dimensions: int = 1024

@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    log_level: str = "INFO"
    cors_origins: list = field(default_factory=lambda: ["*"])

@dataclass
class ChatConfig:
    """Chat model configuration"""
    provider: str = "ollama"
    model: str = "qwen2.5:1.5b"
    base_url: str = "http://localhost:11434"
    context_limit: int = 3000
    max_chunks: int = 5

@dataclass
class AppConfig:
    """Main application configuration"""
    vector_db: VectorDBConfig = field(default_factory=VectorDBConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    api: APIConfig = field(default_factory=APIConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)
    environment: str = "development"

class ConfigManager:
    """Configuration manager with multi-source loading"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[AppConfig] = None
        
    def load_config(self) -> AppConfig:
        """Load configuration from multiple sources"""
        if self._config is not None:
            return self._config
            
        # Load .env file if exists
        load_dotenv()
        
        # Determine config file path
        config_file_path = self._get_config_file_path()
        
        # Load from file if exists
        file_config = {}
        if config_file_path and config_file_path.exists():
            file_config = self._load_config_file(config_file_path)
        
        # Create config with defaults
        config_data = self._merge_configs(file_config)
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Create and validate config object
        self._config = self._create_config_object(config_data)
        self._validate_config(self._config)
        
        return self._config
    
    def _get_config_file_path(self) -> Optional[Path]:
        """Determine config file path from multiple sources"""
        # 1. Explicit path provided
        if self.config_path:
            return Path(self.config_path)
        
        # 2. Environment variable
        env_config_path = os.getenv("CONFIG_PATH")
        if env_config_path:
            return Path(env_config_path)
        
        # 3. Look for config files in current directory
        current_dir = Path.cwd()
        for filename in ["config.yaml", "config.yml", "config.json"]:
            config_file = current_dir / filename
            if config_file.exists():
                return config_file
        
        # 4. Look in config directory
        config_dir = current_dir / "config"
        if config_dir.exists():
            for filename in ["config.yaml", "config.yml", "config.json"]:
                config_file = config_dir / filename
                if config_file.exists():
                    return config_file
        
        return None
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(file) or {}
                elif config_path.suffix.lower() == '.json':
                    return json.load(file) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config file {config_path}: {e}")
    
    def _merge_configs(self, file_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge file config with defaults"""
        default_config = {
            "vector_db": {
                "provider": "qdrant",
                "url": "",
                "api_key": "",
                "collection": "TestCollection6",
                "timeout": 30
            },
            "embedding": {
                "provider": "ollama",
                "model": "bge-m3",
                "base_url": "http://localhost:11434",
                "api_key": "",
                "dimensions": 1024
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8001,
                "reload": False,
                "log_level": "INFO",
                "cors_origins": ["*"]
            },
            "chat": {
                "provider": "ollama",
                "model": "qwen2.5:1.5b",
                "base_url": "http://localhost:11434",
                "context_limit": 3000,
                "max_chunks": 5
            },
            "environment": "development"
        }
        
        # Deep merge
        merged = self._deep_merge(default_config, file_config)
        return merged
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override config with environment variables"""
        # Vector DB config
        if os.getenv("QDRANT_URL"):
            config_data["vector_db"]["url"] = os.getenv("QDRANT_URL")
        if os.getenv("QDRANT_API_KEY"):
            config_data["vector_db"]["api_key"] = os.getenv("QDRANT_API_KEY")
        if os.getenv("QDRANT_COLLECTION"):
            config_data["vector_db"]["collection"] = os.getenv("QDRANT_COLLECTION")
        if os.getenv("VECTOR_DB_PROVIDER"):
            config_data["vector_db"]["provider"] = os.getenv("VECTOR_DB_PROVIDER")
        
        # Embedding config
        if os.getenv("EMBEDDING_PROVIDER"):
            config_data["embedding"]["provider"] = os.getenv("EMBEDDING_PROVIDER")
        if os.getenv("EMBEDDING_MODEL"):
            config_data["embedding"]["model"] = os.getenv("EMBEDDING_MODEL")
        if os.getenv("OLLAMA_BASE_URL"):
            config_data["embedding"]["base_url"] = os.getenv("OLLAMA_BASE_URL")
        if os.getenv("OPENAI_API_KEY"):
            config_data["embedding"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        # API config
        if os.getenv("API_HOST"):
            config_data["api"]["host"] = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            config_data["api"]["port"] = int(os.getenv("API_PORT"))
        if os.getenv("LOG_LEVEL"):
            config_data["api"]["log_level"] = os.getenv("LOG_LEVEL")
        if os.getenv("ENVIRONMENT"):
            config_data["environment"] = os.getenv("ENVIRONMENT")
        # Chat config
        if os.getenv("CHAT_PROVIDER"):
            config_data["chat"]["provider"] = os.getenv("CHAT_PROVIDER")
        if os.getenv("CHAT_MODEL"):
            config_data["chat"]["model"] = os.getenv("CHAT_MODEL")
        if os.getenv("CHAT_BASE_URL"):
            config_data["chat"]["base_url"] = os.getenv("CHAT_BASE_URL")
        if os.getenv("CHAT_CONTEXT_LIMIT"):
            config_data["chat"]["context_limit"] = int(os.getenv("CHAT_CONTEXT_LIMIT"))
        if os.getenv("CHAT_MAX_CHUNKS"):
            config_data["chat"]["max_chunks"] = int(os.getenv("CHAT_MAX_CHUNKS"))
        
        return config_data
    
    def _create_config_object(self, config_data: Dict[str, Any]) -> AppConfig:
        """Create AppConfig object from dictionary"""
        vector_db_config = VectorDBConfig(**config_data["vector_db"])
        embedding_config = EmbeddingConfig(**config_data["embedding"])
        api_config = APIConfig(**config_data["api"])
        chat_config = ChatConfig(**config_data["chat"])
        
        return AppConfig(
            vector_db=vector_db_config,
            embedding=embedding_config,
            api=api_config,
            chat=chat_config,
            environment=config_data["environment"]
        )
    
    def _validate_config(self, config: AppConfig) -> None:
        """Validate configuration"""
        errors = []
        
        # Validate vector DB config
        if not config.vector_db.url:
            errors.append("Vector DB URL is required (set QDRANT_URL or config file)")
        if not config.vector_db.api_key and "localhost" not in config.vector_db.url:
            errors.append("Vector DB API key is required for cloud instances")
        
        # Validate embedding config
        if config.embedding.provider == "openai" and not config.embedding.api_key:
            errors.append("OpenAI API key is required for OpenAI embedding provider")
        
        # Validate API config
        if not (1024 <= config.api.port <= 65535):
            errors.append(f"API port must be between 1024-65535, got {config.api.port}")
        
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors))

# Global config manager instance
config_manager = ConfigManager()

def get_config() -> AppConfig:
    """Get the application configuration"""
    return config_manager.load_config()

def reload_config(config_path: Optional[str] = None) -> AppConfig:
    """Reload configuration"""
    global config_manager
    config_manager = ConfigManager(config_path)
    return config_manager.load_config()
