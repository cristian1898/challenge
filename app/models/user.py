"""User model."""

import enum
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.database import Base


class UserRole(str, enum.Enum):
    """User roles."""
    
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        index=True,
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        nullable=False,
        default=UserRole.USER,
        index=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    
    __table_args__ = (
        Index("ix_users_role_active", "role", "active"),
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_last_name_first_name", "last_name", "first_name"),
    )
    
    @validates("username")
    def validate_username(self, key: str, username: str) -> str:
        """Validate username."""
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(username) > 50:
            raise ValueError("Username must not exceed 50 characters")
        if not username.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return username.lower().strip()
    
    @validates("email")
    def validate_email(self, key: str, email: str) -> str:
        """Validate email."""
        if not email or "@" not in email:
            raise ValueError("Invalid email format")
        return email.lower().strip()
    
    @validates("first_name", "last_name")
    def validate_names(self, key: str, value: str) -> str:
        """Validate name."""
        if not value or len(value.strip()) < 1:
            raise ValueError(f"{key.replace('_', ' ').title()} is required")
        if len(value) > 100:
            raise ValueError(f"{key.replace('_', ' ').title()} must not exceed 100 characters")
        return value.strip()
    
    @property
    def full_name(self) -> str:
        """Full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Admin check."""
        return self.role == UserRole.ADMIN
    
    def to_dict(self) -> dict:
        """To dict."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "active": self.active,
        }
    
    def __str__(self) -> str:
        """Str."""
        return f"User(id={self.id}, username={self.username}, email={self.email})"
