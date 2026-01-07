"""
Pytest Configuration and Fixtures

Provides shared fixtures for all tests including database sessions,
test client, and factory fixtures for creating test data.
"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base, get_db_session
from app.main import app
from app.models.user import User, UserRole


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Override settings for testing
def get_test_settings() -> Settings:
    """Get test-specific settings."""
    return Settings(
        environment="testing",
        database_url=TEST_DATABASE_URL,
        debug=True,
        log_level="DEBUG",
        secret_key="test-secret-key-for-testing-only-min-32-chars",
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_engine, db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_settings] = get_test_settings
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(test_engine, db_session) -> Generator[TestClient, None, None]:
    """Create a synchronous test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_settings] = get_test_settings
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


# Factory fixtures for creating test data

class UserFactory:
    """Factory for creating test users."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._counter = 0
    
    async def create(
        self,
        username: str = None,
        email: str = None,
        first_name: str = "Test",
        last_name: str = "User",
        role: UserRole = UserRole.USER,
        active: bool = True,
    ) -> User:
        """Create a test user in the database."""
        self._counter += 1
        
        if username is None:
            username = f"testuser{self._counter}"
        if email is None:
            email = f"testuser{self._counter}@example.com"
        
        user = User(
            id=str(uuid4()),
            username=username.lower(),
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            role=role,
            active=active,
        )
        
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        
        return user
    
    async def create_batch(self, count: int, **kwargs) -> list[User]:
        """Create multiple test users."""
        users = []
        for i in range(count):
            user = await self.create(
                username=f"batchuser{self._counter + i}",
                email=f"batchuser{self._counter + i}@example.com",
                **kwargs,
            )
            users.append(user)
        return users


@pytest_asyncio.fixture
async def user_factory(db_session) -> UserFactory:
    """Provide a user factory for tests."""
    return UserFactory(db_session)


@pytest_asyncio.fixture
async def sample_user(user_factory) -> User:
    """Create a sample user for tests."""
    return await user_factory.create(
        username="sampleuser",
        email="sample@example.com",
        first_name="Sample",
        last_name="User",
        role=UserRole.USER,
        active=True,
    )


@pytest_asyncio.fixture
async def admin_user(user_factory) -> User:
    """Create an admin user for tests."""
    return await user_factory.create(
        username="adminuser",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        active=True,
    )


@pytest_asyncio.fixture
async def inactive_user(user_factory) -> User:
    """Create an inactive user for tests."""
    return await user_factory.create(
        username="inactiveuser",
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        role=UserRole.USER,
        active=False,
    )


# Test data fixtures

@pytest.fixture
def valid_user_data() -> dict:
    """Return valid user creation data."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
        "role": "user",
        "active": True,
    }


@pytest.fixture
def invalid_user_data_samples() -> list[dict]:
    """Return various invalid user data samples for testing validation."""
    return [
        # Empty username
        {
            "username": "",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
        # Invalid email
        {
            "username": "testuser",
            "email": "not-an-email",
            "first_name": "Test",
            "last_name": "User",
        },
        # Username too short
        {
            "username": "ab",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        },
        # Invalid role
        {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "invalid_role",
        },
        # Missing required fields
        {
            "username": "testuser",
        },
    ]
