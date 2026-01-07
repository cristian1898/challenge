"""Main app module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_db, init_db
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.routers import health_router, users_router
from app.utils.exceptions import AppException
from app.utils.logger import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """App lifespan."""
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """Create app."""
    app = FastAPI(
        title=settings.app_name,
        description="""
## User Management API

A production-ready RESTful API for user management built with FastAPI.

### Features

- **Complete CRUD Operations**: Create, Read, Update, and Delete users
- **Pagination & Filtering**: Efficient data retrieval with query parameters
- **Input Validation**: Comprehensive validation using Pydantic v2
- **Async Database**: Non-blocking database operations with SQLAlchemy 2.0
- **Health Checks**: Kubernetes-ready health endpoints
- **Structured Logging**: JSON logging with correlation IDs
- **OpenAPI Documentation**: Auto-generated API documentation

### Authentication

This API currently does not require authentication. 
Future versions may include JWT-based authentication.

### Rate Limiting

Rate limiting may be applied in production environments.
Check response headers for rate limit information.
        """,
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else "/openapi.json",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Add custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Register routers
    app.include_router(health_router)
    app.include_router(users_router, prefix="/api/v1")
    
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle app exceptions."""
        logger.warning(
            "Application exception",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle validation errors."""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(
            "Validation error",
            path=request.url.path,
            errors=errors,
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"errors": errors},
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected errors."""
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        
        # Don't expose internal errors in production
        message = str(exc) if settings.debug else "An unexpected error occurred"
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": message,
                }
            },
        )


# Create application instance
app = create_application()


# Root endpoint
@app.get(
    "/",
    summary="API Root",
    description="Returns basic API information and links to documentation.",
    tags=["Root"],
)
async def root() -> dict:
    """Root."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "User Management REST API",
        "documentation": {
            "openapi": "/openapi.json",
            "swagger": "/docs" if settings.debug else None,
            "redoc": "/redoc" if settings.debug else None,
        },
        "endpoints": {
            "users": "/api/v1/users",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
