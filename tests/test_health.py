"""
Health Endpoint Tests

Tests for health check and readiness probe endpoints.
"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_liveness_probe(self, client: AsyncClient):
        """Test Kubernetes liveness probe."""
        response = await client.get("/health/live")
        
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
    
    @pytest.mark.asyncio
    async def test_readiness_probe(self, client: AsyncClient):
        """Test Kubernetes readiness probe."""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
    
    @pytest.mark.asyncio
    async def test_detailed_health(self, client: AsyncClient):
        """Test detailed health check endpoint."""
        response = await client.get("/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "application" in data
        assert "name" in data["application"]
        assert "version" in data["application"]
        assert "environment" in data["application"]


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
