"""
Health Check Router Module

Provides endpoints for application health monitoring and diagnostics.
Essential for container orchestration and load balancer health checks.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, status
from sqlalchemy import text

from app.config import settings
from app.database import async_session_factory

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    description="Basic health check endpoint for load balancers and orchestration.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-06T10:30:00Z",
                    }
                }
            },
        },
    },
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check.
    
    Returns:
        Health status with timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/health/live",
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint.",
    responses={
        200: {"description": "Service is alive"},
    },
)
async def liveness() -> Dict[str, str]:
    """
    Liveness probe for Kubernetes.
    
    Returns:
        Alive status
    """
    return {"status": "alive"}


@router.get(
    "/health/ready",
    summary="Readiness probe",
    description="""
    Kubernetes readiness probe endpoint.
    
    Checks database connectivity to determine if the service
    is ready to handle requests.
    """,
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service is not ready"},
    },
)
async def readiness() -> Dict[str, Any]:
    """
    Readiness probe for Kubernetes.
    
    Checks:
    - Database connectivity
    
    Returns:
        Ready status with component health
    """
    checks = {
        "database": await _check_database(),
    }
    
    all_healthy = all(check["healthy"] for check in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/health/detailed",
    summary="Detailed health check",
    description="""
    Comprehensive health check with detailed system information.
    
    Includes:
    - Application info (name, version, environment)
    - Database connectivity status
    - System timestamp
    """,
    responses={
        200: {"description": "Detailed health information"},
    },
)
async def detailed_health() -> Dict[str, Any]:
    """
    Detailed health check with system information.
    
    Returns:
        Comprehensive health status
    """
    db_check = await _check_database()
    
    return {
        "status": "healthy" if db_check["healthy"] else "degraded",
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
        },
        "checks": {
            "database": db_check,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def _check_database() -> Dict[str, Any]:
    """
    Check database connectivity.
    
    Returns:
        Database health status
    """
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            return {
                "healthy": True,
                "latency_ms": None,  # Could add timing
                "message": "Connected",
            }
    except Exception as e:
        return {
            "healthy": False,
            "latency_ms": None,
            "message": str(e),
        }
