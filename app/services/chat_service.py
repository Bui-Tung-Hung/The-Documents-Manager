"""
Chat service using provider pattern
"""

from typing import List, Dict, Any, Optional
from ..core.config import AppConfig, get_config
from ..core.exceptions import ChatError, SearchError
from ..providers.base import ChatProvider, SearchResult
from ..providers.chat.ollama import OllamaChatProvider
from .search_service import get_search_service, SearchService

class ChatService:
    """Chat service that orchestrates search and chat providers"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or get_config()
        self.chat_provider: Optional[ChatProvider] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the chat service with providers"""
        try:
            # Initialize chat provider (using same config as embedding for Ollama)
            self.chat_provider = self._create_chat_provider()
            await self.chat_provider.initialize()
            
            self._initialized = True
            
        except Exception as e:
            raise ChatError(f"Failed to initialize chat service: {e}")
    
    def _create_chat_provider(self) -> ChatProvider:
        """Create chat provider based on config"""
        # For now, only Ollama is supported
        return OllamaChatProvider(self.config.embedding)
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of chat provider"""
        health = {}
        
        try:
            if self.chat_provider:
                health["chat"] = await self.chat_provider.health_check()
            else:
                health["chat"] = False
        except Exception as e:
            print(f"Chat health check error: {e}")
            health["chat"] = False
        
        return health
    
    async def chat_with_files(
        self, 
        file_ids: List[str], 
        message: str, 
        max_chunks: int = 5
    ) -> Dict[str, Any]:
        """Chat with specific files using RAG approach"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Get search service
            search_service = await get_search_service()
            
            # Search for relevant chunks in specified files
            relevant_chunks = await search_service.search_with_file_filter(
                query=message,
                file_ids=file_ids,
                limit=max_chunks
            )
            
            # Build context from chunks
            context = self._build_context(relevant_chunks, max_tokens=3000)
            
            # Generate response using chat provider
            response = await self.chat_provider.generate_response(context, message)
            
            # Format chunks for response
            source_chunks = [
                {
                    "file_id": chunk.file_id,
                    "content": chunk.content,
                    "score": chunk.score
                }
                for chunk in relevant_chunks
            ]
            
            return {
                "response": response,
                "source_chunks": source_chunks,
                "total_chunks": len(source_chunks)
            }
            
        except Exception as e:
            raise ChatError(f"Failed to chat with files: {e}")
    
    def _build_context(self, chunks: List[SearchResult], max_tokens: int = 3000) -> str:
        """Build context string from search results with token limit"""
        if not chunks:
            return ""
        
        context_parts = []
        current_tokens = 0
        
        for chunk in chunks:
            # Rough token estimation (1 token ≈ 4 characters for Vietnamese)
            chunk_tokens = len(chunk.content) // 4
            
            if current_tokens + chunk_tokens > max_tokens:
                # Truncate the chunk to fit
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 50:  # Only add if meaningful content
                    truncated_content = chunk.content[:remaining_tokens * 4]
                    context_parts.append(f"[File: {chunk.file_id}]\n{truncated_content}...")
                break
            
            context_parts.append(f"[File: {chunk.file_id}]\n{chunk.content}")
            current_tokens += chunk_tokens
        
        return "\n\n".join(context_parts)
    
    async def close(self) -> None:
        """Close all connections"""
        if hasattr(self.chat_provider, 'close'):
            await self.chat_provider.close()

# Global chat service instance
_chat_service: Optional[ChatService] = None

async def get_chat_service() -> ChatService:
    """Get or create global chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
        await _chat_service.initialize()
    return _chat_service
