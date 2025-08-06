"""
Ollama embedding provider implementation
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from ...core.config import EmbeddingConfig
from ...core.exceptions import EmbeddingError
from ..base import EmbeddingProvider

class OllamaProvider(EmbeddingProvider):
    """Ollama embedding provider"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.session: aiohttp.ClientSession = None
        
    async def initialize(self) -> None:
        """Initialize Ollama provider"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            if not await self.health_check():
                raise EmbeddingError("Ollama health check failed")
                
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize Ollama provider: {e}")
    
    async def health_check(self) -> bool:
        """Check if Ollama is healthy"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if our model is available
                    models = [model["name"] for model in data.get("models", [])]
                    return any(self.config.model in model for model in models)
                return False
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.session:
            await self.initialize()
        
        try:
            embeddings = []
            
            for text in texts:
                payload = {
                    "model": self.config.model,
                    "prompt": text
                }
                
                async with self.session.post(
                    f"{self.config.base_url}/api/embeddings",
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise EmbeddingError(f"Ollama API returned status {response.status}")
                    
                    data = await response.json()
                    embedding = data.get("embedding", [])
                    
                    if not embedding:
                        raise EmbeddingError("No embedding returned from Ollama")
                    
                    embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}")
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings"""
        # BGE-M3 model has 1024 dimensions
        if "bge-m3" in self.config.model:
            return 1024
        # Default fallback, should be detected dynamically in real implementation
        return self.config.dimensions
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "provider": "ollama",
            "model": self.config.model,
            "base_url": self.config.base_url,
            "dimensions": self.get_dimension()
        }
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
