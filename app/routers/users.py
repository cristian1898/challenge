"""
Users Router Module

Defines all REST API endpoints for user management.
Implements full CRUD operations with proper HTTP semantics.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.schemas.user import (
    UserCreate,
    UserFilters,
    UserListResponse,
    UserResponse,
    UserRole,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.exceptions import AppException

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(session)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="""
    Create a new user with the provided information.
    
    - **username**: Must be unique, 3-50 characters, alphanumeric with underscores/hyphens
    - **email**: Must be unique and a valid email format
    - **first_name**: User's first name (1-100 characters)
    - **last_name**: User's last name (1-100 characters)
    - **role**: User role (admin, user, guest). Defaults to 'user'
    - **active**: Account status. Defaults to True
    """,
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Username or email already exists"},
        422: {"description": "Validation error"},
    },
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        service: User service instance
        
    Returns:
        Created user
    """
    try:
        return await service.create_user(user_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
    description="""
    Retrieve a paginated list of users with optional filtering.
    
    **Pagination:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    
    **Filtering:**
    - `username`: Filter by username (partial match)
    - `email`: Filter by email (partial match)
    - `first_name`: Filter by first name (partial match)
    - `last_name`: Filter by last name (partial match)
    - `role`: Filter by role (exact match)
    - `active`: Filter by active status
    - `search`: Search across all text fields
    
    **Sorting:**
    - `sort_by`: Field to sort by (default: created_at)
    - `sort_desc`: Sort descending (default: true)
    """,
    responses={
        200: {"description": "List of users with pagination metadata"},
    },
)
async def list_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    username: Optional[str] = Query(default=None, description="Filter by username"),
    email: Optional[str] = Query(default=None, description="Filter by email"),
    first_name: Optional[str] = Query(default=None, description="Filter by first name"),
    last_name: Optional[str] = Query(default=None, description="Filter by last name"),
    role: Optional[UserRole] = Query(default=None, description="Filter by role"),
    active: Optional[bool] = Query(default=None, description="Filter by active status"),
    search: Optional[str] = Query(default=None, description="Search across fields"),
    sort_by: str = Query(default="created_at", description="Field to sort by"),
    sort_desc: bool = Query(default=True, description="Sort descending"),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """
    List users with pagination and filtering.
    
    Args:
        page: Page number
        page_size: Items per page
        username: Username filter
        email: Email filter
        first_name: First name filter
        last_name: Last name filter
        role: Role filter
        active: Active status filter
        search: Search term
        sort_by: Sort field
        sort_desc: Sort direction
        service: User service instance
        
    Returns:
        Paginated list of users
    """
    filters = UserFilters(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        active=active,
        search=search,
    )
    
    return await service.list_users(
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )


@router.get(
    "/statistics",
    summary="Get user statistics",
    description="Get aggregate statistics about users in the system.",
    responses={
        200: {"description": "User statistics"},
    },
)
async def get_statistics(
    service: UserService = Depends(get_user_service),
) -> dict:
    """
    Get user statistics.
    
    Args:
        service: User service instance
        
    Returns:
        Dictionary with user statistics
    """
    return await service.get_user_statistics()


@router.get(
    "/by-username/{username}",
    response_model=UserResponse,
    summary="Get user by username",
    description="Retrieve a user by their unique username.",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get a user by username.
    
    Args:
        username: User's username
        service: User service instance
        
    Returns:
        User data
    """
    try:
        return await service.get_user_by_username(username)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.get(
    "/by-email/{email}",
    response_model=UserResponse,
    summary="Get user by email",
    description="Retrieve a user by their email address.",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get a user by email.
    
    Args:
        email: User's email address
        service: User service instance
        
    Returns:
        User data
    """
    try:
        return await service.get_user_by_email(email)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a user by their unique identifier.",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Get a user by ID.
    
    Args:
        user_id: User's unique identifier
        service: User service instance
        
    Returns:
        User data
    """
    try:
        return await service.get_user(user_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="""
    Update an existing user's information.
    
    Only provided fields will be updated (partial update).
    At least one field must be provided.
    """,
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Username or email conflict"},
        422: {"description": "Validation error"},
    },
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update a user.
    
    Args:
        user_id: User's unique identifier
        user_data: Update data
        service: User service instance
        
    Returns:
        Updated user data
    """
    try:
        return await service.update_user(user_id, user_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partial update user",
    description="""
    Partially update an existing user's information.
    
    Same as PUT - only provided fields will be updated.
    """,
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Username or email conflict"},
        422: {"description": "Validation error"},
    },
)
async def partial_update_user(
    user_id: str,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Partially update a user (alias for PUT).
    
    Args:
        user_id: User's unique identifier
        user_data: Update data
        service: User service instance
        
    Returns:
        Updated user data
    """
    try:
        return await service.update_user(user_id, user_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Permanently delete a user from the system.",
    responses={
        204: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Delete a user.
    
    Args:
        user_id: User's unique identifier
        service: User service instance
    """
    try:
        await service.delete_user(user_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.post(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user",
    description="Deactivate a user account (soft delete).",
    responses={
        200: {"description": "User deactivated successfully"},
        404: {"description": "User not found"},
    },
)
async def deactivate_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Deactivate a user.
    
    Args:
        user_id: User's unique identifier
        service: User service instance
        
    Returns:
        Updated user data
    """
    try:
        return await service.deactivate_user(user_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user",
    description="Activate a previously deactivated user account.",
    responses={
        200: {"description": "User activated successfully"},
        404: {"description": "User not found"},
    },
)
async def activate_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Activate a user.
    
    Args:
        user_id: User's unique identifier
        service: User service instance
        
    Returns:
        Updated user data
    """
    try:
        return await service.activate_user(user_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.to_dict()["error"])
