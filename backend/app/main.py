"""
Main FastAPI application initialization and configuration.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings, db_manager
from app.schemas.base import ErrorResponse
from app.controllers import (
    auth_router,
    meeting_router,
    context_router,
    notification_router
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-Powered Meeting Context Assistant",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Security middleware - Allow localhost and common development hosts
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", settings.APP_NAME]
        )
    
    # Custom exception handler
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An internal server error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request.headers.get("X-Request-ID", "unknown")
            }
        )
    
    # Startup event
    @app.on_event("startup")
    async def startup():
        """Initialize database on startup."""
        try:
            await db_manager.initialize()
            logger.info(f"Application started in {settings.ENVIRONMENT} mode")
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown():
        """Cleanup resources on shutdown."""
        try:
            await db_manager.dispose()
            logger.info("Application shutdown")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.ENVIRONMENT
        }
    
    # Register API routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(meeting_router, prefix="/api/v1")
    app.include_router(context_router, prefix="/api/v1")
    app.include_router(notification_router, prefix="/api/v1")
    
    # API v1 root endpoint
    @app.get("/api/v1")
    async def api_root():
        """API root endpoint."""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "endpoints": {
                "auth": "/api/v1/auth",
                "meetings": "/api/v1/meetings",
                "contexts": "/api/v1/contexts",
                "notifications": "/api/v1/notifications",
                "docs": "/docs" if settings.DEBUG else None
            }
        }
    
    logger.info("FastAPI application configured successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
