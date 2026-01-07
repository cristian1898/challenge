"""
User Service Unit Tests

Tests for the UserService business logic layer.
Uses mocked repository for isolation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserFilters
from app.services.user_service import UserService
from app.utils.exceptions import ConflictException, NotFoundException


class TestUserServiceCreate:
    """Tests for UserService.create_user method."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session):
        """Test successful user creation through service."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            first_name="New",
            last_name="User",
            role=UserRole.USER,
            active=True,
        )
        
        result = await service.create_user(user_data)
        
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.first_name == "New"
        assert result.last_name == "User"
        assert result.role == UserRole.USER
        assert result.active is True
        assert result.id is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, db_session, sample_user):
        """Test that duplicate username raises ConflictException."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username=sample_user.username,
            email="different@example.com",
            first_name="Test",
            last_name="User",
        )
        
        with pytest.raises(ConflictException) as exc_info:
            await service.create_user(user_data)
        
        assert "already taken" in str(exc_info.value.message)
        assert exc_info.value.status_code == 409
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session, sample_user):
        """Test that duplicate email raises ConflictException."""
        service = UserService(db_session)
        
        user_data = UserCreate(
            username="differentuser",
            email=sample_user.email,
            first_name="Test",
            last_name="User",
        )
        
        with pytest.raises(ConflictException) as exc_info:
            await service.create_user(user_data)
        
        assert "already registered" in str(exc_info.value.message)
        assert exc_info.value.status_code == 409


class TestUserServiceGet:
    """Tests for UserService get methods."""
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, db_session, sample_user):
        """Test getting user by ID."""
        service = UserService(db_session)
        
        result = await service.get_user(sample_user.id)
        
        assert result.id == sample_user.id
        assert result.username == sample_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, db_session):
        """Test that non-existent user raises NotFoundException."""
        service = UserService(db_session)
        
        with pytest.raises(NotFoundException) as exc_info:
            await service.get_user("non-existent-id")
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session, sample_user):
        """Test getting user by username."""
        service = UserService(db_session)
        
        result = await service.get_user_by_username(sample_user.username)
        
        assert result.username == sample_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session, sample_user):
        """Test getting user by email."""
        service = UserService(db_session)
        
        result = await service.get_user_by_email(sample_user.email)
        
        assert result.email == sample_user.email


class TestUserServiceList:
    """Tests for UserService.list_users method."""
    
    @pytest.mark.asyncio
    async def test_list_users_empty(self, db_session):
        """Test listing users when none exist."""
        service = UserService(db_session)
        
        result = await service.list_users()
        
        assert result.data == []
        assert result.meta.total == 0
    
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, db_session, user_factory):
        """Test pagination in list_users."""
        await user_factory.create_batch(25)
        service = UserService(db_session)
        
        # First page
        result = await service.list_users(page=1, page_size=10)
        
        assert len(result.data) == 10
        assert result.meta.total == 25
        assert result.meta.page == 1
        assert result.meta.total_pages == 3
        assert result.meta.has_next is True
        assert result.meta.has_prev is False
        
        # Last page
        result = await service.list_users(page=3, page_size=10)
        
        assert len(result.data) == 5
        assert result.meta.has_next is False
        assert result.meta.has_prev is True
    
    @pytest.mark.asyncio
    async def test_list_users_with_filters(self, db_session, sample_user, admin_user):
        """Test filtering in list_users."""
        service = UserService(db_session)
        
        filters = UserFilters(role=UserRole.ADMIN)
        result = await service.list_users(filters=filters)
        
        assert len(result.data) == 1
        assert result.data[0].role == UserRole.ADMIN


class TestUserServiceUpdate:
    """Tests for UserService.update_user method."""
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, db_session, sample_user):
        """Test successful user update."""
        service = UserService(db_session)
        
        update_data = UserUpdate(first_name="Updated", last_name="Name")
        result = await service.update_user(sample_user.id, update_data)
        
        assert result.first_name == "Updated"
        assert result.last_name == "Name"
        assert result.username == sample_user.username
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, db_session):
        """Test updating non-existent user raises NotFoundException."""
        service = UserService(db_session)
        
        update_data = UserUpdate(first_name="Test")
        
        with pytest.raises(NotFoundException):
            await service.update_user("non-existent-id", update_data)
    
    @pytest.mark.asyncio
    async def test_update_user_username_conflict(self, db_session, sample_user, admin_user):
        """Test updating to existing username raises ConflictException."""
        service = UserService(db_session)
        
        update_data = UserUpdate(username=admin_user.username)
        
        with pytest.raises(ConflictException) as exc_info:
            await service.update_user(sample_user.id, update_data)
        
        assert "already taken" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_update_user_same_username_allowed(self, db_session, sample_user):
        """Test user can update with same username (no conflict with self)."""
        service = UserService(db_session)
        
        update_data = UserUpdate(username=sample_user.username, first_name="Updated")
        result = await service.update_user(sample_user.id, update_data)
        
        assert result.first_name == "Updated"


class TestUserServiceDelete:
    """Tests for UserService.delete_user method."""
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session, sample_user):
        """Test successful user deletion."""
        service = UserService(db_session)
        
        result = await service.delete_user(sample_user.id)
        
        assert result is True
        
        # Verify user is deleted
        with pytest.raises(NotFoundException):
            await service.get_user(sample_user.id)
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, db_session):
        """Test deleting non-existent user raises NotFoundException."""
        service = UserService(db_session)
        
        with pytest.raises(NotFoundException):
            await service.delete_user("non-existent-id")


class TestUserServiceActivation:
    """Tests for user activation/deactivation."""
    
    @pytest.mark.asyncio
    async def test_deactivate_user(self, db_session, sample_user):
        """Test user deactivation."""
        service = UserService(db_session)
        
        result = await service.deactivate_user(sample_user.id)
        
        assert result.active is False
    
    @pytest.mark.asyncio
    async def test_activate_user(self, db_session, inactive_user):
        """Test user activation."""
        service = UserService(db_session)
        
        result = await service.activate_user(inactive_user.id)
        
        assert result.active is True


class TestUserServiceStatistics:
    """Tests for UserService.get_user_statistics method."""
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, db_session, sample_user, admin_user, inactive_user):
        """Test getting user statistics."""
        service = UserService(db_session)
        
        stats = await service.get_user_statistics()
        
        assert stats["total_users"] == 3
        assert stats["active_users"] == 2
        assert stats["inactive_users"] == 1
        assert stats["by_role"]["admin"] == 1
        assert stats["by_role"]["user"] == 2
