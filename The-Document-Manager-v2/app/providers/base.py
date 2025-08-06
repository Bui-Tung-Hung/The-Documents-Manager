"""
Abstract base classes for providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Search result data structure"""
    file_id: str
    score: float
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Document:
    """Document data structure for indexing"""
    content: str
    file_id: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class VectorDBProvider(ABC):
    """Abstract base class for vector database providers"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector database connection"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vector database is healthy"""
        pass
    
    @abstractmethod
    async def create_collection(self, collection_name: str, dimension: int) -> None:
        """Create a collection in the vector database"""
        pass
    
    @abstractmethod
    async def upsert_documents(self, collection_name: str, documents: List[Document], embeddings: List[List[float]]) -> None:
        """Insert or update documents with their embeddings"""
        pass
    
    @abstractmethod
    async def search(self, collection_name: str, query_embedding: List[float], limit: int = 10) -> List[SearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_documents(self, collection_name: str, file_ids: List[str]) -> None:
        """Delete documents by file IDs"""
        pass
    
    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        pass

class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the embedding provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the embedding provider is healthy"""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get the dimension of embeddings"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        pass
