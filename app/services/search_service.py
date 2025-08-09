"""
Search service using provider pattern
"""

import asyncio
from typing import List, Dict, Any, Optional
from collections import defaultdict

from ..core.config import AppConfig, get_config
from ..core.exceptions import SearchError, ProviderError
from ..providers.base import VectorDBProvider, EmbeddingProvider, SearchResult, Document
from ..providers.vector_db.qdrant import QdrantProvider
from ..providers.embedding.ollama import OllamaProvider

class SearchService:
    """Search service that orchestrates vector DB and embedding providers"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or get_config()
        self.vector_db: Optional[VectorDBProvider] = None
        self.embedding: Optional[EmbeddingProvider] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the search service with providers"""
        try:
            # Initialize vector DB provider
            self.vector_db = self._create_vector_db_provider()
            await self.vector_db.initialize()
            
            # Initialize embedding provider
            self.embedding = self._create_embedding_provider()
            await self.embedding.initialize()
            
            # Ensure collection exists
            dimension = self.embedding.get_dimension()
            await self.vector_db.create_collection(
                self.config.vector_db.collection, 
                dimension
            )
            
            self._initialized = True
            
        except Exception as e:
            raise SearchError(f"Failed to initialize search service: {e}")
    
    def _create_vector_db_provider(self) -> VectorDBProvider:
        """Create vector DB provider based on config"""
        provider_name = self.config.vector_db.provider.lower()
        
        if provider_name == "qdrant":
            return QdrantProvider(self.config.vector_db)
        else:
            raise ProviderError(f"Unsupported vector DB provider: {provider_name}")
    
    def _create_embedding_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on config"""
        provider_name = self.config.embedding.provider.lower()
        
        if provider_name == "ollama":
            return OllamaProvider(self.config.embedding)
        else:
            raise ProviderError(f"Unsupported embedding provider: {provider_name}")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health = {}
        
        try:
            if self.vector_db:
                health["vector_db"] = await self.vector_db.health_check()
            else:
                health["vector_db"] = False
                
            if self.embedding:
                health["embedding"] = await self.embedding.health_check()
            else:
                health["embedding"] = False
                
        except Exception as e:
            print(f"Health check error: {e}")
            health["vector_db"] = False
            health["embedding"] = False
        
        return health
    
    async def index_documents(self, documents: List[Document]) -> None:
        """Index documents into the vector database"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embeddings for all documents
            texts = [doc.content for doc in documents]
            embeddings = await self.embedding.embed_texts(texts)
            
            # Upsert into vector database
            await self.vector_db.upsert_documents(
                self.config.vector_db.collection,
                documents,
                embeddings
            )
            
        except Exception as e:
            raise SearchError(f"Failed to index documents: {e}")
    
    async def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for documents similar to the query"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embedding for query
            query_embedding = await self.embedding.embed_text(query)
            
            # Search in vector database
            results = await self.vector_db.search(
                self.config.vector_db.collection,
                query_embedding,
                limit
            )
            
            return results
            
        except Exception as e:
            raise SearchError(f"Failed to search documents: {e}")
    
    async def search_by_file_id(self, query: str, k: int = 50, top_files: int = 5) -> List[Dict[str, Any]]:
        """Search and group results by file_id, similar to original implementation"""
        try:
            # Get search results
            raw_results = await self.search(query, k)
            
            # Group by file_id and get best score for each
            file_scores = defaultdict(lambda: {"score": 0.0, "content": ""})
            
            for result in raw_results:
                file_id = result.file_id
                if result.score > file_scores[file_id]["score"]:
                    file_scores[file_id] = {
                        "score": result.score,
                        "content": result.content
                    }
            
            # Sort by score and take top files
            sorted_files = sorted(
                file_scores.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )[:top_files]
            
            # Format results
            results = []
            for file_id, data in sorted_files:
                results.append({
                    "file_id": file_id,
                    "score": data["score"],
                    "content": data["content"]
                })
            
            return results
            
        except Exception as e:
            raise SearchError(f"Failed to search by file_id: {e}")
    
    async def search_with_file_filter(self, query: str, file_ids: List[str], limit: int = 10) -> List[SearchResult]:
        """Search for documents similar to the query within specified files"""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Generate embedding for query
            query_embedding = await self.embedding.embed_text(query)
            
            # Search in vector database with file filter
            results = await self.vector_db.search_with_filter(
                self.config.vector_db.collection,
                query_embedding,
                file_ids,
                limit
            )
            
            return results
            
        except Exception as e:
            raise SearchError(f"Failed to search documents with file filter: {e}")
    
    async def delete_documents(self, file_ids: List[str]) -> None:
        """Delete documents by file IDs"""
        if not self._initialized:
            await self.initialize()
        
        try:
            await self.vector_db.delete_documents(
                self.config.vector_db.collection,
                file_ids
            )
        except Exception as e:
            raise SearchError(f"Failed to delete documents: {e}")
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not self._initialized:
            await self.initialize()
        
        try:
            return await self.vector_db.get_collection_info(
                self.config.vector_db.collection
            )
        except Exception as e:
            raise SearchError(f"Failed to get collection info: {e}")
    
    async def close(self) -> None:
        """Close all connections"""
        if hasattr(self.embedding, 'close'):
            await self.embedding.close()

# Global search service instance
_search_service: Optional[SearchService] = None

async def get_search_service() -> SearchService:
    """Get or create global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
        await _search_service.initialize()
    return _search_service
