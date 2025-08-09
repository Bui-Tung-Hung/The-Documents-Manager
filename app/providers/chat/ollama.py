"""
Ollama chat provider implementation
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any
from ...core.config import EmbeddingConfig
from ...core.exceptions import ChatError
from ..base import ChatProvider

class OllamaChatProvider(ChatProvider):
    """Ollama chat provider"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.session: aiohttp.ClientSession = None
        self.chat_model = "qwen2.5:1.5b"  # Fixed chat model
        
    async def initialize(self) -> None:
        """Initialize Ollama chat provider"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            if not await self.health_check():
                raise ChatError("Ollama chat health check failed")
                
        except Exception as e:
            raise ChatError(f"Failed to initialize Ollama chat provider: {e}")
    
    async def health_check(self) -> bool:
        """Check if Ollama chat is healthy"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(f"{self.config.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if our chat model is available
                    models = [model["name"] for model in data.get("models", [])]
                    return any(self.chat_model in model for model in models)
                return False
        except Exception as e:
            print(f"Ollama chat health check failed: {e}")
            return False
    
    async def generate_response(self, context: str, message: str) -> str:
        """Generate chat response given context and message"""
        if not self.session:
            await self.initialize()
        
        try:
            # Build prompt template
            prompt = self._build_prompt(context, message)
            
            payload = {
                "model": self.chat_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    raise ChatError(f"Ollama API returned status {response.status}")
                
                data = await response.json()
                response_text = data.get("response", "")
                
                if not response_text:
                    return "Không thể tạo phản hồi từ mô hình."
                
                return response_text.strip()
                
        except Exception as e:
            raise ChatError(f"Failed to generate chat response: {e}")
    
    def _build_prompt(self, context: str, message: str) -> str:
        """Build prompt template for chat"""
        if not context.strip():
            return f"""Câu hỏi: {message}

Trả lời: Không tìm thấy thông tin liên quan trong tài liệu."""
        
        return f"""Dựa trên các thông tin sau đây từ tài liệu:

{context}

Câu hỏi: {message}

Hãy trả lời câu hỏi dựa trên thông tin được cung cấp. Nếu không tìm thấy thông tin liên quan, hãy trả lời "Không tìm thấy thông tin liên quan trong tài liệu."

Trả lời:"""
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the chat model"""
        return {
            "provider": "ollama",
            "model": self.chat_model,
            "base_url": self.config.base_url,
            "type": "chat"
        }
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
