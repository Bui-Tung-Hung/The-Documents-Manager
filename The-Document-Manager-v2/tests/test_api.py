"""
Tests for API routes
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import create_app

@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)

def test_root_endpoint(client):
    """Test root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Document Search API v2 - Flexible & Modular"
    assert data["version"] == "2.0.0"
    assert "endpoints" in data

@patch('app.services.search_service.get_search_service')
def test_health_endpoint_healthy(mock_get_service, client):
    """Test health endpoint when services are healthy"""
    # Mock search service
    mock_service = AsyncMock()
    mock_service.health_check.return_value = {
        "vector_db": True,
        "embedding": True
    }
    mock_get_service.return_value = mock_service
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["services"]["vector_db"] == True
    assert data["services"]["embedding"] == True

@patch('app.services.search_service.get_search_service')
def test_search_files_endpoint(mock_get_service, client):
    """Test search files endpoint"""
    # Mock search service
    mock_service = AsyncMock()
    mock_service.search_by_file_id.return_value = [
        {
            "file_id": "doc_001",
            "score": 0.95,
            "content": "Machine learning content"
        }
    ]
    mock_get_service.return_value = mock_service
    
    response = client.post(
        "/search-files",
        json={"query": "machine learning"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "machine learning"
    assert len(data["results"]) == 1
    assert data["results"][0]["file_id"] == "doc_001"

def test_search_files_validation_error(client):
    """Test search files endpoint with invalid input"""
    response = client.post(
        "/search-files",
        json={"query": ""}  # Empty query should fail validation
    )
    assert response.status_code == 422
