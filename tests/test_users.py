"""
User API Endpoint Tests

Comprehensive tests for all user CRUD endpoints.
Tests cover success cases, error cases, and edge cases.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


class TestCreateUser:
    """Tests for POST /api/v1/users endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient, valid_user_data: dict):
        """Test successful user creation."""
        response = await client.post("/api/v1/users", json=valid_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["username"] == valid_user_data["username"].lower()
        assert data["email"] == valid_user_data["email"].lower()
        assert data["first_name"] == valid_user_data["first_name"]
        assert data["last_name"] == valid_user_data["last_name"]
        assert data["role"] == valid_user_data["role"]
        assert data["active"] == valid_user_data["active"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_user_default_role(self, client: AsyncClient):
        """Test that default role is 'user' when not specified."""
        user_data = {
            "username": "defaultrole",
            "email": "default@example.com",
            "first_name": "Default",
            "last_name": "Role",
        }
        
        response = await client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 201
        assert response.json()["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(
        self, client: AsyncClient, sample_user: User, valid_user_data: dict
    ):
        """Test that duplicate username returns 409."""
        valid_user_data["username"] = sample_user.username
        valid_user_data["email"] = "different@example.com"
        
        response = await client.post("/api/v1/users", json=valid_user_data)
        
        assert response.status_code == 409
        assert "already taken" in response.json()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self, client: AsyncClient, sample_user: User, valid_user_data: dict
    ):
        """Test that duplicate email returns 409."""
        valid_user_data["username"] = "differentuser"
        valid_user_data["email"] = sample_user.email
        
        response = await client.post("/api/v1/users", json=valid_user_data)
        
        assert response.status_code == 409
        assert "already registered" in response.json()["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, client: AsyncClient):
        """Test that invalid email returns 422."""
        user_data = {
            "username": "validuser",
            "email": "not-an-email",
            "first_name": "Test",
            "last_name": "User",
        }
        
        response = await client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_user_username_too_short(self, client: AsyncClient):
        """Test that username too short returns 422."""
        user_data = {
            "username": "ab",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        
        response = await client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_user_normalizes_username(self, client: AsyncClient):
        """Test that username is normalized to lowercase."""
        user_data = {
            "username": "TestUser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        
        response = await client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_create_user_all_roles(self, client: AsyncClient):
        """Test creating users with all role types."""
        roles = ["admin", "user", "guest"]
        
        for i, role in enumerate(roles):
            user_data = {
                "username": f"roletest{i}",
                "email": f"roletest{i}@example.com",
                "first_name": "Role",
                "last_name": "Test",
                "role": role,
            }
            
            response = await client.post("/api/v1/users", json=user_data)
            
            assert response.status_code == 201
            assert response.json()["role"] == role


class TestGetUser:
    """Tests for GET /api/v1/users/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, client: AsyncClient, sample_user: User):
        """Test successful user retrieval by ID."""
        response = await client.get(f"/api/v1/users/{sample_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == sample_user.id
        assert data["username"] == sample_user.username
        assert data["email"] == sample_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Test that non-existent user returns 404."""
        response = await client.get("/api/v1/users/non-existent-id")
        
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, client: AsyncClient, sample_user: User):
        """Test user retrieval by username."""
        response = await client.get(f"/api/v1/users/by-username/{sample_user.username}")
        
        assert response.status_code == 200
        assert response.json()["username"] == sample_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, client: AsyncClient, sample_user: User):
        """Test user retrieval by email."""
        response = await client.get(f"/api/v1/users/by-email/{sample_user.email}")
        
        assert response.status_code == 200
        assert response.json()["email"] == sample_user.email


class TestListUsers:
    """Tests for GET /api/v1/users endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_users_empty(self, client: AsyncClient):
        """Test listing users when database is empty."""
        response = await client.get("/api/v1/users")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"] == []
        assert data["meta"]["total"] == 0
    
    @pytest.mark.asyncio
    async def test_list_users_with_data(self, client: AsyncClient, user_factory):
        """Test listing users with data."""
        await user_factory.create_batch(5)
        
        response = await client.get("/api/v1/users")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 5
        assert data["meta"]["total"] == 5
    
    @pytest.mark.asyncio
    async def test_list_users_pagination(self, client: AsyncClient, user_factory):
        """Test pagination works correctly."""
        await user_factory.create_batch(15)
        
        # First page
        response = await client.get("/api/v1/users?page=1&page_size=10")
        data = response.json()
        
        assert len(data["data"]) == 10
        assert data["meta"]["page"] == 1
        assert data["meta"]["total"] == 15
        assert data["meta"]["has_next"] is True
        assert data["meta"]["has_prev"] is False
        
        # Second page
        response = await client.get("/api/v1/users?page=2&page_size=10")
        data = response.json()
        
        assert len(data["data"]) == 5
        assert data["meta"]["page"] == 2
        assert data["meta"]["has_next"] is False
        assert data["meta"]["has_prev"] is True
    
    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(
        self, client: AsyncClient, sample_user: User, admin_user: User
    ):
        """Test filtering by role."""
        response = await client.get("/api/v1/users?role=admin")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 1
        assert data["data"][0]["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_list_users_filter_by_active(
        self, client: AsyncClient, sample_user: User, inactive_user: User
    ):
        """Test filtering by active status."""
        response = await client.get("/api/v1/users?active=false")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 1
        assert data["data"][0]["active"] is False
    
    @pytest.mark.asyncio
    async def test_list_users_search(self, client: AsyncClient, sample_user: User):
        """Test search functionality."""
        response = await client.get(f"/api/v1/users?search={sample_user.first_name}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) >= 1
        assert any(u["first_name"] == sample_user.first_name for u in data["data"])
    
    @pytest.mark.asyncio
    async def test_list_users_sorting(self, client: AsyncClient, user_factory):
        """Test sorting functionality."""
        await user_factory.create(username="aaa_user")
        await user_factory.create(username="zzz_user")
        
        # Sort ascending
        response = await client.get("/api/v1/users?sort_by=username&sort_desc=false")
        data = response.json()
        
        usernames = [u["username"] for u in data["data"]]
        assert usernames == sorted(usernames)


class TestUpdateUser:
    """Tests for PUT /api/v1/users/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, client: AsyncClient, sample_user: User):
        """Test successful user update."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
        }
        
        response = await client.put(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["username"] == sample_user.username  # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient):
        """Test updating non-existent user returns 404."""
        update_data = {"first_name": "Test"}
        
        response = await client.put("/api/v1/users/non-existent-id", json=update_data)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_user_username_conflict(
        self, client: AsyncClient, sample_user: User, admin_user: User
    ):
        """Test updating username to existing one returns 409."""
        update_data = {"username": admin_user.username}
        
        response = await client.put(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_update_user_email_conflict(
        self, client: AsyncClient, sample_user: User, admin_user: User
    ):
        """Test updating email to existing one returns 409."""
        update_data = {"email": admin_user.email}
        
        response = await client.put(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_update_user_role(self, client: AsyncClient, sample_user: User):
        """Test updating user role."""
        update_data = {"role": "admin"}
        
        response = await client.put(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        assert response.json()["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_partial_update_user(self, client: AsyncClient, sample_user: User):
        """Test PATCH endpoint for partial update."""
        update_data = {"first_name": "Patched"}
        
        response = await client.patch(f"/api/v1/users/{sample_user.id}", json=update_data)
        
        assert response.status_code == 200
        assert response.json()["first_name"] == "Patched"


class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{id} endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, client: AsyncClient, sample_user: User):
        """Test successful user deletion."""
        response = await client.delete(f"/api/v1/users/{sample_user.id}")
        
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = await client.get(f"/api/v1/users/{sample_user.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, client: AsyncClient):
        """Test deleting non-existent user returns 404."""
        response = await client.delete("/api/v1/users/non-existent-id")
        
        assert response.status_code == 404


class TestUserActivation:
    """Tests for user activation/deactivation endpoints."""
    
    @pytest.mark.asyncio
    async def test_deactivate_user(self, client: AsyncClient, sample_user: User):
        """Test user deactivation."""
        response = await client.post(f"/api/v1/users/{sample_user.id}/deactivate")
        
        assert response.status_code == 200
        assert response.json()["active"] is False
    
    @pytest.mark.asyncio
    async def test_activate_user(self, client: AsyncClient, inactive_user: User):
        """Test user activation."""
        response = await client.post(f"/api/v1/users/{inactive_user.id}/activate")
        
        assert response.status_code == 200
        assert response.json()["active"] is True
    
    @pytest.mark.asyncio
    async def test_deactivate_not_found(self, client: AsyncClient):
        """Test deactivating non-existent user."""
        response = await client.post("/api/v1/users/non-existent-id/deactivate")
        
        assert response.status_code == 404


class TestUserStatistics:
    """Tests for GET /api/v1/users/statistics endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_statistics(
        self, client: AsyncClient, sample_user: User, admin_user: User, inactive_user: User
    ):
        """Test statistics endpoint."""
        response = await client.get("/api/v1/users/statistics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert "by_role" in data
        assert data["total_users"] == 3
        assert data["active_users"] == 2
        assert data["inactive_users"] == 1
