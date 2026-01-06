"""
User Schemas Module

Defines Pydantic models for request/response validation and serialization.
Implements strict validation rules with detailed error messages.
"""

import re
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserRole(str, Enum):
    """User role enumeration matching database enum."""
    
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserBase(BaseModel):
    """
    Base schema with common user fields.
    
    Provides shared validation logic for all user-related schemas.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "active": True,
            }
        }
    )
    
    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="Unique username (3-50 characters, alphanumeric with underscores/hyphens)",
            examples=["john_doe", "jane-smith"]
        )
    ]
    
    email: Annotated[
        EmailStr,
        Field(
            description="Valid email address",
            examples=["john.doe@example.com"]
        )
    ]
    
    first_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="User's first name",
            examples=["John"]
        )
    ]
    
    last_name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="User's last name",
            examples=["Doe"]
        )
    ]
    
    role: Annotated[
        UserRole,
        Field(
            default=UserRole.USER,
            description="User role in the system",
            examples=["user", "admin", "guest"]
        )
    ]
    
    active: Annotated[
        bool,
        Field(
            default=True,
            description="Whether the user account is active",
            examples=[True]
        )
    ]
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.
        
        Rules:
        - Must be 3-50 characters
        - Can only contain letters, numbers, underscores, and hyphens
        - Cannot start or end with underscore or hyphen
        - Cannot have consecutive underscores or hyphens
        """
        if not v:
            raise ValueError("Username is required")
        
        v = v.lower().strip()
        
        # Check valid characters
        if not re.match(r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$|^[a-z0-9]$", v):
            raise ValueError(
                "Username must start and end with a letter or number, "
                "and can only contain letters, numbers, underscores, and hyphens"
            )
        
        # Check for consecutive special characters
        if "--" in v or "__" in v or "-_" in v or "_-" in v:
            raise ValueError("Username cannot have consecutive underscores or hyphens")
        
        return v
    
    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str, info) -> str:
        """
        Validate name fields.
        
        Rules:
        - Must contain only letters, spaces, hyphens, and apostrophes
        - Must start with a letter
        """
        if not v:
            field_name = info.field_name.replace("_", " ").title()
            raise ValueError(f"{field_name} is required")
        
        v = v.strip()
        
        # Allow letters, spaces, hyphens, and apostrophes for names like "O'Brien" or "Mary-Jane"
        if not re.match(r"^[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ\s\-\']*$", v):
            field_name = info.field_name.replace("_", " ").title()
            raise ValueError(
                f"{field_name} must contain only letters, spaces, hyphens, and apostrophes"
            )
        
        return v.title()
    
    @field_validator("email")
    @classmethod
    def validate_email_lowercase(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower().strip() if v else v


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    All fields from UserBase are required except role and active
    which have defaults.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "active": True,
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    
    All fields are optional - only provided fields will be updated.
    Implements partial update (PATCH) semantics.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "first_name": "Johnny",
                "last_name": "Doe",
                "active": False,
            }
        }
    )
    
    username: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=3,
            max_length=50,
            description="New username"
        )
    ]
    
    email: Annotated[
        Optional[EmailStr],
        Field(default=None, description="New email address")
    ]
    
    first_name: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=1,
            max_length=100,
            description="New first name"
        )
    ]
    
    last_name: Annotated[
        Optional[str],
        Field(
            default=None,
            min_length=1,
            max_length=100,
            description="New last name"
        )
    ]
    
    role: Annotated[
        Optional[UserRole],
        Field(default=None, description="New role")
    ]
    
    active: Annotated[
        Optional[bool],
        Field(default=None, description="New active status")
    ]
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username if provided."""
        if v is None:
            return v
        
        v = v.lower().strip()
        
        if not re.match(r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$|^[a-z0-9]$", v):
            raise ValueError(
                "Username must start and end with a letter or number"
            )
        
        if "--" in v or "__" in v:
            raise ValueError("Username cannot have consecutive underscores or hyphens")
        
        return v
    
    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str], info) -> Optional[str]:
        """Validate name if provided."""
        if v is None:
            return v
        
        v = v.strip()
        
        if not re.match(r"^[a-zA-ZÀ-ÿ][a-zA-ZÀ-ÿ\s\-\']*$", v):
            field_name = info.field_name.replace("_", " ").title()
            raise ValueError(f"{field_name} must contain only letters")
        
        return v.title()
    
    @field_validator("email")
    @classmethod
    def validate_email_lowercase(cls, v: Optional[str]) -> Optional[str]:
        """Normalize email to lowercase if provided."""
        return v.lower().strip() if v else v
    
    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdate":
        """Ensure at least one field is provided for update."""
        values = [
            self.username,
            self.email,
            self.first_name,
            self.last_name,
            self.role,
            self.active,
        ]
        if all(v is None for v in values):
            raise ValueError("At least one field must be provided for update")
        return self


class UserResponse(BaseModel):
    """
    Schema for user response data.
    
    Includes all user fields plus computed fields.
    Used for single user responses.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "user",
                "created_at": "2024-01-06T10:30:00Z",
                "updated_at": "2024-01-06T10:30:00Z",
                "active": True,
            }
        }
    )
    
    id: str = Field(description="Unique user identifier")
    username: str = Field(description="User's username")
    email: str = Field(description="User's email address")
    first_name: str = Field(description="User's first name")
    last_name: str = Field(description="User's last name")
    role: UserRole = Field(description="User's role")
    created_at: datetime = Field(description="Account creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    active: bool = Field(description="Account active status")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class UserListResponse(BaseModel):
    """
    Schema for paginated user list response.
    
    Includes pagination metadata and list of users.
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john.doe@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": "user",
                        "created_at": "2024-01-06T10:30:00Z",
                        "updated_at": "2024-01-06T10:30:00Z",
                        "active": True,
                    }
                ],
                "meta": {
                    "total": 100,
                    "page": 1,
                    "page_size": 20,
                    "total_pages": 5,
                    "has_next": True,
                    "has_prev": False,
                },
            }
        }
    )
    
    data: List[UserResponse] = Field(description="List of users")
    meta: PaginationMeta = Field(description="Pagination metadata")


class UserFilters(BaseModel):
    """
    Schema for filtering users in list operations.
    
    All fields are optional and can be combined.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    username: Optional[str] = Field(
        default=None,
        description="Filter by username (partial match)"
    )
    email: Optional[str] = Field(
        default=None,
        description="Filter by email (partial match)"
    )
    first_name: Optional[str] = Field(
        default=None,
        description="Filter by first name (partial match)"
    )
    last_name: Optional[str] = Field(
        default=None,
        description="Filter by last name (partial match)"
    )
    role: Optional[UserRole] = Field(
        default=None,
        description="Filter by role"
    )
    active: Optional[bool] = Field(
        default=None,
        description="Filter by active status"
    )
    search: Optional[str] = Field(
        default=None,
        description="Search across username, email, first_name, last_name"
    )
