"""
User Repository Module

Implements the Repository pattern for User data access.
Provides a clean abstraction layer between business logic and database operations.
"""

from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserFilters, UserUpdate


class UserRepository:
    """
    Repository for User database operations.
    
    Provides CRUD operations and query methods for User entities.
    All methods are async and require an AsyncSession.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
    
    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user in the database.
        
        Args:
            user_data: Validated user creation data
            
        Returns:
            Created User instance
            
        Raises:
            IntegrityError: If username or email already exists
        """
        user = User(
            id=str(uuid4()),
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=UserRole(user_data.role) if isinstance(user_data.role, str) else user_data.role,
            active=user_data.active,
        )
        
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User instance if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.
        
        Args:
            username: User's username
            
        Returns:
            User instance if found, None otherwise
        """
        stmt = select(User).where(User.username == username.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email.
        
        Args:
            email: User's email address
            
        Returns:
            User instance if found, None otherwise
        """
        stmt = select(User).where(User.email == email.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[UserFilters] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Tuple[List[User], int]:
        """
        Retrieve paginated list of users with optional filtering.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Optional filter criteria
            sort_by: Field to sort by
            sort_desc: Sort in descending order if True
            
        Returns:
            Tuple of (list of users, total count)
        """
        # Base query
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # Apply filters
        if filters:
            conditions = self._build_filter_conditions(filters)
            if conditions:
                stmt = stmt.where(and_(*conditions))
                count_stmt = count_stmt.where(and_(*conditions))
        
        # Get total count
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_desc:
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute query
        result = await self._session.execute(stmt)
        users = list(result.scalars().all())
        
        return users, total
    
    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id: User's unique identifier
            user_data: Validated update data
            
        Returns:
            Updated User instance if found, None otherwise
            
        Raises:
            IntegrityError: If updated username or email conflicts with existing user
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)
        
        for field, value in update_data.items():
            if field == "role" and isinstance(value, str):
                value = UserRole(value)
            setattr(user, field, value)
        
        await self._session.flush()
        await self._session.refresh(user)
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user was deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        await self._session.delete(user)
        await self._session.flush()
        
        return True
    
    async def exists_by_username(self, username: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if a username is already taken.
        
        Args:
            username: Username to check
            exclude_id: Optional user ID to exclude from check (for updates)
            
        Returns:
            True if username exists, False otherwise
        """
        stmt = select(func.count(User.id)).where(User.username == username.lower())
        
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        
        result = await self._session.execute(stmt)
        count = result.scalar() or 0
        
        return count > 0
    
    async def exists_by_email(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if an email is already taken.
        
        Args:
            email: Email to check
            exclude_id: Optional user ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        stmt = select(func.count(User.id)).where(User.email == email.lower())
        
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        
        result = await self._session.execute(stmt)
        count = result.scalar() or 0
        
        return count > 0
    
    async def count_by_role(self, role: UserRole) -> int:
        """
        Count users with a specific role.
        
        Args:
            role: Role to count
            
        Returns:
            Number of users with the role
        """
        stmt = select(func.count(User.id)).where(User.role == role)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def count_active(self) -> int:
        """
        Count active users.
        
        Returns:
            Number of active users
        """
        stmt = select(func.count(User.id)).where(User.active == True)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    def _build_filter_conditions(self, filters: UserFilters) -> List:
        """
        Build SQLAlchemy filter conditions from filter schema.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List of SQLAlchemy conditions
        """
        conditions = []
        
        if filters.username:
            conditions.append(User.username.ilike(f"%{filters.username}%"))
        
        if filters.email:
            conditions.append(User.email.ilike(f"%{filters.email}%"))
        
        if filters.first_name:
            conditions.append(User.first_name.ilike(f"%{filters.first_name}%"))
        
        if filters.last_name:
            conditions.append(User.last_name.ilike(f"%{filters.last_name}%"))
        
        if filters.role:
            role_value = filters.role if isinstance(filters.role, UserRole) else UserRole(filters.role)
            conditions.append(User.role == role_value)
        
        if filters.active is not None:
            conditions.append(User.active == filters.active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                )
            )
        
        return conditions
