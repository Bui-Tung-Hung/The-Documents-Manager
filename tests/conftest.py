"""
Test configuration for pytest
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "file_id": "doc_001",
            "metadata": {"category": "ai", "priority": "high"}
        },
        {
            "content": "Deep learning uses neural networks with multiple layers.",
            "file_id": "doc_002", 
            "metadata": {"category": "ml", "priority": "medium"}
        }
    ]
