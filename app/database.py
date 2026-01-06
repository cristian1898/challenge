"""Database configuration."""

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
    """SQLAlchemy base."""
    
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    
    def __repr__(self) -> str:
        """Repr."""
        class_name = self.__class__.__name__
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        )
        return f"{class_name}({attrs})"


def create_engine_instance() -> AsyncEngine:
    """Create db engine."""
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
    """Get db session."""
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
    """Get db context."""
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
    """Init db."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close db."""
    await engine.dispose()


async def check_db_connection() -> bool:
    """Check db connection."""
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False
