"""
Qdrant vector database provider implementation
"""

import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import ResponseHandlingException

from ..base import VectorDBProvider, SearchResult, Document
from ...core.config import VectorDBConfig
from ...core.exceptions import VectorDBError

class QdrantProvider(VectorDBProvider):
    """Qdrant vector database provider"""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.client: Optional[QdrantClient] = None
        
    async def initialize(self) -> None:
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(
                url=self.config.url,
                api_key=self.config.api_key if self.config.api_key else None,
                timeout=self.config.timeout
            )
            
            # Test connection
            await self.health_check()
            
        except Exception as e:
            raise VectorDBError(f"Failed to initialize Qdrant client: {e}")
    
    async def health_check(self) -> bool:
        """Check if Qdrant is healthy"""
        if not self.client:
            return False
            
        try:
            # Run in thread pool since qdrant-client is sync
            loop = asyncio.get_event_loop()
            collections = await loop.run_in_executor(
                None, 
                self.client.get_collections
            )
            return True
        except Exception as e:
            print(f"Qdrant health check failed: {e}")
            return False
    
    async def create_collection(self, collection_name: str, dimension: int) -> None:
        """Create a collection in Qdrant"""
        if not self.client:
            raise VectorDBError("Qdrant client not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Check if collection exists
            try:
                await loop.run_in_executor(
                    None,
                    self.client.get_collection,
                    collection_name
                )
                print(f"Collection {collection_name} already exists")
                return
            except ResponseHandlingException as e:
                # Collection doesn't exist, create it
                if "not found" not in str(e).lower():
                    # If error is not "not found", re-raise
                    raise
            
            # Create collection
            await loop.run_in_executor(
                None,
                self.client.create_collection,
                collection_name,
                models.VectorParams(
                    size=dimension,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Created collection {collection_name}")
            
        except Exception as e:
            # If collection already exists (409 error), ignore it
            if "already exists" in str(e):
                print(f"Collection {collection_name} already exists - continuing")
                return
            raise VectorDBError(f"Failed to create collection {collection_name}: {e}")
    
    async def upsert_documents(self, collection_name: str, documents: List[Document], embeddings: List[List[float]]) -> None:
        """Insert or update documents with their embeddings"""
        if not self.client:
            raise VectorDBError("Qdrant client not initialized")
        
        if len(documents) != len(embeddings):
            raise VectorDBError("Number of documents must match number of embeddings")
        
        try:
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # Generate unique ID based on file_id and content hash
                point_id = hash(f"{doc.file_id}:{doc.content[:100]}") % (2**31)
                
                point = models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "file_id": doc.file_id,
                        "content": doc.content,
                        **doc.metadata
                    }
                )
                points.append(point)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client.upsert,
                collection_name,
                points
            )
            
        except Exception as e:
            raise VectorDBError(f"Failed to upsert documents: {e}")
    
    async def search(self, collection_name: str, query_embedding: List[float], limit: int = 10) -> List[SearchResult]:
        """Search for similar documents"""
        if not self.client:
            raise VectorDBError("Qdrant client not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Use direct method call for qdrant-client
            search_result = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
            )
            
            results = []
            for hit in search_result:
                payload = hit.payload
                # Handle both file_id and fileID for compatibility
                file_id = payload.get("file_id") or payload.get("fileID", "")
                # Handle different content field names
                content = payload.get("page_content") or payload.get("content") or payload.get("text") or payload.get("Content", "")
                result = SearchResult(
                    file_id=file_id,
                    score=hit.score,
                    content=content,
                    metadata={k: v for k, v in payload.items() if k not in ["file_id", "fileID", "page_content", "content", "text", "Content"]}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            raise VectorDBError(f"Failed to search documents: {e}")
    
    async def delete_documents(self, collection_name: str, file_ids: List[str]) -> None:
        """Delete documents by file IDs"""
        if not self.client:
            raise VectorDBError("Qdrant client not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Delete by filter
            await loop.run_in_executor(
                None,
                self.client.delete,
                collection_name,
                models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_id",
                            match=models.MatchAny(any=file_ids)
                        )
                    ]
                )
            )
            
        except Exception as e:
            raise VectorDBError(f"Failed to delete documents: {e}")
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        if not self.client:
            raise VectorDBError("Qdrant client not initialized")
        
        try:
            loop = asyncio.get_event_loop()
            collection_info = await loop.run_in_executor(
                None,
                self.client.get_collection,
                collection_name
            )
            
            return {
                "name": collection_name,
                "status": collection_info.status,
                "vectors_count": collection_info.vectors_count,
                "config": {
                    "params": collection_info.config.params.dict() if collection_info.config.params else None,
                    "hnsw_config": collection_info.config.hnsw_config.dict() if collection_info.config.hnsw_config else None,
                    "optimizer_config": collection_info.config.optimizer_config.dict() if collection_info.config.optimizer_config else None,
                }
            }
            
        except Exception as e:
            raise VectorDBError(f"Failed to get collection info: {e}")
