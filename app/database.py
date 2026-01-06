"""
Database Configuration Module

Implements async database connectivity using SQLAlchemy 2.0 with proper
session management, connection pooling, and lifecycle handling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.config import settings

# Naming convention for constraints to ensure consistent migration names
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    Provides common functionality and metadata configuration
    for all database models in the application.
    """
    
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    
    def __repr__(self) -> str:
        """Generate a readable representation of the model instance."""
        class_name = self.__class__.__name__
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        )
        return f"{class_name}({attrs})"


def create_engine_instance() -> AsyncEngine:
    """
    Create and configure the async database engine.
    
    Handles different database backends (PostgreSQL, SQLite) with
    appropriate connection pool settings.
    
    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    is_sqlite = settings.database_url.startswith("sqlite")
    
    engine_kwargs = {
        "echo": settings.database_echo,
    }
    
    if is_sqlite:
        # SQLite specific configuration for async support
        engine_kwargs.update({
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        })
    else:
        # PostgreSQL connection pool configuration
        engine_kwargs.update({
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_pre_ping": True,  # Verify connections before use
            "pool_recycle": 3600,   # Recycle connections after 1 hour
        })
    
    engine = create_async_engine(
        settings.async_database_url,
        **engine_kwargs
    )
    
    return engine


# Global engine instance
engine = create_engine_instance()

# Session factory with recommended settings
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI that provides a database session.
    
    Creates a new session for each request and ensures proper
    cleanup after the request is complete.
    
    Yields:
        AsyncSession: Database session for the current request
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of request context.
    
    Useful for background tasks, CLI commands, and testing.
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    Should be called during application startup to ensure
    all tables exist before handling requests.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close all database connections.
    
    Should be called during application shutdown to ensure
    clean resource cleanup.
    """
    await engine.dispose()


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
