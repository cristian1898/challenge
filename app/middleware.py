"""
Middleware Module

Implements custom middleware for request processing, logging,
and security headers.
"""

import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import get_logger, set_correlation_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs:
    - Request method, path, and client IP
    - Response status code and processing time
    - Correlation ID for request tracing
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with logging.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        set_correlation_id(correlation_id)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params) if request.query_params else None,
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent"),
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log unhandled exception
            process_time = time.perf_counter() - start_time
            logger.error(
                "Request failed with unhandled exception",
                method=request.method,
                path=request.url.path,
                duration_ms=round(process_time * 1000, 2),
                error=str(e),
                exc_info=True,
            )
            raise
        
        # Calculate processing time
        process_time = time.perf_counter() - start_time
        
        # Log response
        log_method = logger.info if response.status_code < 400 else logger.warning
        log_method(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )
        
        # Add custom headers to response
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Implements OWASP recommended security headers.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Add security headers to response.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        
        # Remove server header if present
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
