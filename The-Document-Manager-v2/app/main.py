"""
Main FastAPI application
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .core.config import get_config
from .core.exceptions import ConfigurationError
from .api.routes import router
from .services.search_service import get_search_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("🚀 Starting Document Search API v2...")
    
    try:
        # Load and validate configuration
        config = get_config()
        logger.info(f"✅ Configuration loaded for environment: {config.environment}")
        
        # Initialize search service
        try:
            search_service = await get_search_service()
            logger.info("✅ Search service initialized")
            
            # Check health
            health = await search_service.health_check()
            if all(health.values()):
                logger.info("✅ All services are healthy")
            else:
                logger.warning(f"⚠️ Some services are unhealthy: {health}")
        except Exception as e:
            logger.warning(f"⚠️ Search service initialization failed: {e}")
            logger.info("✅ Continuing without search service pre-initialization")
        
        logger.info(f"🌟 FastAPI server starting on {config.api.host}:{config.api.port}")
        
    except ConfigurationError as e:
        logger.error(f"❌ Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Document Search API v2...")
    try:
        search_service = await get_search_service()
        await search_service.close()
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Load config for app metadata
    try:
        config = get_config()
    except Exception as e:
        logger.error(f"Failed to load config during app creation: {e}")
        # Use defaults for app creation
        config = None
    
    # Create FastAPI app
    app = FastAPI(
        title="Document Search API v2",
        description="AI-Powered Document Search System with Flexible Architecture",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configure CORS
    cors_origins = ["*"]
    if config and config.api.cors_origins:
        cors_origins = config.api.cors_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": str(exc) if config and config.environment == "development" else None
            }
        )
    
    return app

# Create the app instance
app = create_app()

def main():
    """Main entry point for running the application"""
    try:
        config = get_config()
        uvicorn.run(
            "app.main:app",
            host=config.api.host,
            port=config.api.port,
            reload=config.api.reload,
            log_level=config.api.log_level.lower()
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()
