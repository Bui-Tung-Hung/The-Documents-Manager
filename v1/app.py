from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SearchFileRequest, FileSearchResponse, HealthResponse
from search_service import FileSearchService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Search API",
    description="API for searching documents by file_id",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search service
try:
    search_service = FileSearchService()
    logger.info("Search service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize search service: {e}")
    search_service = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if search_service else "unhealthy",
        message="Document Search API is running" if search_service else "Search service not available"
    )


@app.post("/search-files", response_model=FileSearchResponse)
async def search_files(request: SearchFileRequest):
    """
    Search for documents grouped by file_id
    
    Args:
        request: SearchFileRequest containing the query string
        
    Returns:
        FileSearchResponse with query and results
    """
    if not search_service:
        raise HTTPException(
            status_code=503, 
            detail="Search service not available"
        )
    
    try:
        logger.info(f"Searching for query: {request.query}")
        
        # Perform search
        results = search_service.search_by_file_id(
            query=request.query,
            k=50,  # Search more documents to ensure we get diverse file_ids
            top_files=5  # Return top 5 file_ids
        )
        
        logger.info(f"Found {len(results)} file_id results")
        
        return FileSearchResponse(
            query=request.query,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/search-files",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
