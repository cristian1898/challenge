"""
Schema Validation Tests

Tests for Pydantic schema validation logic.
"""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate, UserRole


class TestUserCreateValidation:
    """Tests for UserCreate schema validation."""
    
    def test_valid_user_create(self):
        """Test creating valid user schema."""
        user = UserCreate(
            username="validuser",
            email="valid@example.com",
            first_name="Valid",
            last_name="User",
        )
        
        assert user.username == "validuser"
        assert user.email == "valid@example.com"
    
    def test_username_lowercase_normalization(self):
        """Test username is normalized to lowercase."""
        user = UserCreate(
            username="ValidUser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        
        assert user.username == "validuser"
    
    def test_email_lowercase_normalization(self):
        """Test email is normalized to lowercase."""
        user = UserCreate(
            username="testuser",
            email="Test@EXAMPLE.com",
            first_name="Test",
            last_name="User",
        )
        
        assert user.email == "test@example.com"
    
    def test_name_title_case_normalization(self):
        """Test names are normalized to title case."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            first_name="john",
            last_name="DOE",
        )
        
        assert user.first_name == "John"
        assert user.last_name == "Doe"
    
    def test_username_too_short(self):
        """Test username validation - too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
        
        assert "username" in str(exc_info.value).lower()
    
    def test_username_too_long(self):
        """Test username validation - too long."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="a" * 51,
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
    
    def test_username_invalid_characters(self):
        """Test username validation - invalid characters."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="test@user!",
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
    
    def test_username_consecutive_special_chars(self):
        """Test username validation - consecutive special characters."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="test__user",
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )
    
    def test_valid_username_with_special_chars(self):
        """Test valid username with allowed special characters."""
        user = UserCreate(
            username="test_user-123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        
        assert user.username == "test_user-123"
    
    def test_invalid_email(self):
        """Test email validation - invalid format."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="not-an-email",
                first_name="Test",
                last_name="User",
            )
    
    def test_first_name_required(self):
        """Test first_name is required."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                first_name="",
                last_name="User",
            )
    
    def test_last_name_required(self):
        """Test last_name is required."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="",
            )
    
    def test_name_with_special_chars(self):
        """Test names with allowed special characters."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            first_name="Mary-Jane",
            last_name="O'Brien",
        )
        
        assert user.first_name == "Mary-Jane"
        assert user.last_name == "O'Brien"
    
    def test_default_role(self):
        """Test default role is USER."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        
        assert user.role == UserRole.USER
    
    def test_default_active(self):
        """Test default active is True."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        
        assert user.active is True
    
    def test_all_roles_valid(self):
        """Test all role values are valid."""
        for role in UserRole:
            user = UserCreate(
                username=f"testuser{role.value}",
                email=f"test{role.value}@example.com",
                first_name="Test",
                last_name="User",
                role=role,
            )
            assert user.role == role


class TestUserUpdateValidation:
    """Tests for UserUpdate schema validation."""
    
    def test_partial_update_single_field(self):
        """Test partial update with single field."""
        update = UserUpdate(first_name="Updated")
        
        assert update.first_name == "Updated"
        assert update.last_name is None
        assert update.username is None
    
    def test_partial_update_multiple_fields(self):
        """Test partial update with multiple fields."""
        update = UserUpdate(
            first_name="Updated",
            last_name="Name",
            role=UserRole.ADMIN,
        )
        
        assert update.first_name == "Updated"
        assert update.last_name == "Name"
        assert update.role == UserRole.ADMIN
    
    def test_empty_update_raises_error(self):
        """Test that update with no fields raises error."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate()
        
        assert "at least one field" in str(exc_info.value).lower()
    
    def test_update_username_validation(self):
        """Test username validation still applies on update."""
        with pytest.raises(ValidationError):
            UserUpdate(username="ab")  # Too short
    
    def test_update_email_validation(self):
        """Test email validation still applies on update."""
        with pytest.raises(ValidationError):
            UserUpdate(email="not-an-email")
    
    def test_update_active_status(self):
        """Test updating active status."""
        update = UserUpdate(active=False)
        
        assert update.active is False
