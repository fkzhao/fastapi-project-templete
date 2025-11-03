from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime
from services.user import UserService

from schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
)
from schemas.base import MessageResponse, APIResponse

router = APIRouter()
user_service = UserService()

@router.post(
    "/",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(user_data: UserCreateRequest):
    """
    Create a new user with the provided data.

    - **name**: User's full name (required)
    - **nick_name**: User's nickname (required)
    - **email**: User's email address (optional)
    """
    # TODO: Implement actual database creation logic
    user = UserResponse(
        id=1,
        name=user_data.name,
        nick_name=user_data.nick_name,
        email=user_data.email,
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    return APIResponse(success=True, data=user, message="User created successfully")


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(user_id: int):
    """
    Retrieve a user by their ID.
    """
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    user = user_service.get_by_id(user_id)
    print(user)
    return UserResponse(
        id=user_id,
        name=user.name,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user"
)
async def update_user(user_id: int, user_data: UserUpdateRequest):
    """
    Update an existing user with the provided data.
    Only provided fields will be updated.
    """
    # TODO: Implement actual database update logic
    return UserResponse(
        id=user_id,
        name=user_data.name or "John Doe",
        nick_name=user_data.nick_name or "johndoe",
        email=user_data.email,
        create_time=datetime.now(),
        update_time=datetime.now()
    )


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user"
)
async def delete_user(user_id: int):
    """
    Delete a user by their ID.
    """
    # TODO: Implement actual database deletion logic
    return MessageResponse(
        message=f"User {user_id} deleted successfully",
        code=200
    )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Get user list"
)
async def get_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    search: str = Query(default=None, description="Search keyword")
):
    """
    Get a paginated list of users.

    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)
    - **search**: Optional search keyword
    """
    # TODO: Implement actual database query with pagination
    users = [
        UserResponse(
            id=1,
            name="John Doe",
            nick_name="johndoe",
            email="john@example.com",
            create_time=datetime.now(),
            update_time=datetime.now()
        ),
        UserResponse(
            id=2,
            name="Jane Smith",
            nick_name="janesmith",
            email="jane@example.com",
            create_time=datetime.now(),
            update_time=datetime.now()
        )
    ]

    return UserListResponse(
        items=users,
        total=2,
        page=page,
        page_size=page_size
    )
