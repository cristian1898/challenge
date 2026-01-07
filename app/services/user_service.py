"""User service."""

import math
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    PaginationMeta,
    UserCreate,
    UserFilters,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.utils.exceptions import ConflictException, NotFoundException, ValidationException
from app.utils.logger import LoggerMixin, get_logger


class UserService(LoggerMixin):
    """User business logic service."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self._session = session
        self._repository = UserRepository(session)
        self._logger = get_logger(self.__class__.__name__)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        self._logger.info(
            "Creating new user",
            username=user_data.username,
            email=user_data.email,
        )
        
        if await self._repository.exists_by_username(user_data.username):
            self._logger.warning(
                "Username already exists",
                username=user_data.username,
            )
            raise ConflictException(
                message=f"Username '{user_data.username}' is already taken",
                field="username",
                value=user_data.username,
            )
        
        if await self._repository.exists_by_email(user_data.email):
            self._logger.warning(
                "Email already exists",
                email=user_data.email,
            )
            raise ConflictException(
                message=f"Email '{user_data.email}' is already registered",
                field="email",
                value=user_data.email,
            )
        
        user = await self._repository.create(user_data)
        
        self._logger.info(
            "User created successfully",
            user_id=user.id,
            username=user.username,
        )
        
        return UserResponse.model_validate(user)
    
    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID."""
        self._logger.debug("Fetching user", user_id=user_id)
        
        user = await self._repository.get_by_id(user_id)
        
        if not user:
            self._logger.warning("User not found", user_id=user_id)
            raise NotFoundException(resource="User", resource_id=user_id)
        
        return UserResponse.model_validate(user)
    
    async def get_user_by_username(self, username: str) -> UserResponse:
        """Get user by username."""
        self._logger.debug("Fetching user by username", username=username)
        
        user = await self._repository.get_by_username(username)
        
        if not user:
            self._logger.warning("User not found", username=username)
            raise NotFoundException(
                resource="User",
                message=f"User with username '{username}' not found",
            )
        
        return UserResponse.model_validate(user)
    
    async def get_user_by_email(self, email: str) -> UserResponse:
        """Get user by email."""
        self._logger.debug("Fetching user by email", email=email)
        
        user = await self._repository.get_by_email(email)
        
        if not user:
            self._logger.warning("User not found", email=email)
            raise NotFoundException(
                resource="User",
                message=f"User with email '{email}' not found",
            )
        
        return UserResponse.model_validate(user)
    
    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[UserFilters] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> UserListResponse:
        """Get paginated list of users."""
        self._logger.debug(
            "Listing users",
            page=page,
            page_size=page_size,
            filters=filters.model_dump() if filters else None,
        )
        
        skip = (page - 1) * page_size
        
        users, total = await self._repository.get_all(
            skip=skip,
            limit=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
        
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        meta = PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        
        self._logger.debug(
            "Users fetched",
            count=len(users),
            total=total,
        )
        
        return UserListResponse(
            data=[UserResponse.model_validate(user) for user in users],
            meta=meta,
        )
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Update an existing user."""
        self._logger.info(
            "Updating user",
            user_id=user_id,
            update_fields=list(user_data.model_dump(exclude_unset=True).keys()),
        )
        
        existing_user = await self._repository.get_by_id(user_id)
        if not existing_user:
            self._logger.warning("User not found for update", user_id=user_id)
            raise NotFoundException(resource="User", resource_id=user_id)
        
        if user_data.username and user_data.username != existing_user.username:
            if await self._repository.exists_by_username(user_data.username, exclude_id=user_id):
                self._logger.warning(
                    "Username conflict on update",
                    username=user_data.username,
                )
                raise ConflictException(
                    message=f"Username '{user_data.username}' is already taken",
                    field="username",
                    value=user_data.username,
                )
        
        if user_data.email and user_data.email != existing_user.email:
            if await self._repository.exists_by_email(user_data.email, exclude_id=user_id):
                self._logger.warning(
                    "Email conflict on update",
                    email=user_data.email,
                )
                raise ConflictException(
                    message=f"Email '{user_data.email}' is already registered",
                    field="email",
                    value=user_data.email,
                )
        
        user = await self._repository.update(user_id, user_data)
        
        self._logger.info(
            "User updated successfully",
            user_id=user_id,
        )
        
        return UserResponse.model_validate(user)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        self._logger.info("Deleting user", user_id=user_id)
        
        existing_user = await self._repository.get_by_id(user_id)
        if not existing_user:
            self._logger.warning("User not found for deletion", user_id=user_id)
            raise NotFoundException(resource="User", resource_id=user_id)
        
        deleted = await self._repository.delete(user_id)
        
        if deleted:
            self._logger.info(
                "User deleted successfully",
                user_id=user_id,
                username=existing_user.username,
            )
        
        return deleted
    
    async def deactivate_user(self, user_id: str) -> UserResponse:
        """Deactivate a user."""
        self._logger.info("Deactivating user", user_id=user_id)
        
        update_data = UserUpdate(active=False)
        return await self.update_user(user_id, update_data)
    
    async def activate_user(self, user_id: str) -> UserResponse:
        """Activate a user."""
        self._logger.info("Activating user", user_id=user_id)
        
        update_data = UserUpdate(active=True)
        return await self.update_user(user_id, update_data)
    
    async def get_user_statistics(self) -> dict:
        """Get user statistics."""
        from app.models.user import UserRole
        
        total_active = await self._repository.count_active()
        admin_count = await self._repository.count_by_role(UserRole.ADMIN)
        user_count = await self._repository.count_by_role(UserRole.USER)
        guest_count = await self._repository.count_by_role(UserRole.GUEST)
        
        _, total = await self._repository.get_all(skip=0, limit=1)
        
        return {
            "total_users": total,
            "active_users": total_active,
            "inactive_users": total - total_active,
            "by_role": {
                "admin": admin_count,
                "user": user_count,
                "guest": guest_count,
            },
        }
