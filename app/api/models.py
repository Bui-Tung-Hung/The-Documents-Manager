"""
Pydantic models for API requests and responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Request models
class SearchFileRequest(BaseModel):
    """Request model for file search"""
    query: str = Field(..., description="Search query text", min_length=1, max_length=1000)

class IndexDocumentsRequest(BaseModel):
    """Request model for indexing documents"""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents to index")

class DeleteDocumentsRequest(BaseModel):
    """Request model for deleting documents"""
    file_ids: List[str] = Field(..., description="List of file IDs to delete")

# Response models
class SearchResultItem(BaseModel):
    """Individual search result item"""
    file_id: str = Field(..., description="File identifier")
    score: float = Field(..., description="Similarity score")
    content: str = Field(..., description="Document content")

class FileSearchResponse(BaseModel):
    """Response model for file search"""
    query: str = Field(..., description="Original search query")
    results: List[SearchResultItem] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall health status")
    message: str = Field(..., description="Health status message")
    services: Optional[Dict[str, bool]] = Field(None, description="Individual service health")

class APIInfoResponse(BaseModel):
    """Response model for API information"""
    message: str = Field(..., description="API welcome message")
    version: str = Field(..., description="API version")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")

class CollectionInfoResponse(BaseModel):
    """Response model for collection information"""
    name: str = Field(..., description="Collection name")
    status: str = Field(..., description="Collection status")
    vectors_count: Optional[int] = Field(None, description="Number of vectors in collection")
    config: Dict[str, Any] = Field(..., description="Collection configuration")

class IndexResponse(BaseModel):
    """Response model for indexing operations"""
    message: str = Field(..., description="Operation result message")
    documents_processed: int = Field(..., description="Number of documents processed")

class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    message: str = Field(..., description="Operation result message")
    deleted_count: int = Field(..., description="Number of documents deleted")

# Error response models
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class ValidationErrorResponse(BaseModel):
    """Validation error response model"""
    error: str = Field(default="validation_error", description="Error type")
    message: str = Field(..., description="Validation error message")
    field_errors: List[Dict[str, Any]] = Field(..., description="Field-specific errors")
