"""
User-related Pydantic schemas for request/response validation.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

from .base import BaseResponse, TimestampSchema


# ============ Request Schemas ============

class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    nick_name: str = Field(..., min_length=1, max_length=50, description="User's nickname")
    email: Optional[EmailStr] = Field(default=None, description="User's email address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "nick_name": "johndoe",
                "email": "john@example.com"
            }
        }
    )


class UserUpdateRequest(BaseModel):
    """Schema for updating an existing user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's full name")
    nick_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's nickname")
    email: Optional[EmailStr] = Field(None, description="User's email address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "nick_name": "janedoe"
            }
        }
    )


class UserQueryParams(BaseModel):
    """Query parameters for user list."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(default=None, description="Search keyword")
    sort_by: Optional[str] = Field(default="id", description="Sort field")
    order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


# ============ Response Schemas ============

class UserResponse(BaseResponse, TimestampSchema):
    """Schema for user response."""
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    nick_name: str = Field(..., description="User's nickname")
    email: Optional[str] = Field(None, description="User's email address")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "nick_name": "johndoe",
                "email": "john@example.com",
                "create_time": "2025-10-28T10:00:00",
                "update_time": "2025-10-28T10:00:00"
            }
        }
    )


class UserBriefResponse(BaseModel):
    """Brief user info (for list views or nested objects)."""
    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User's full name")
    nick_name: str = Field(..., description="User's nickname")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Response for user list with pagination."""
    items: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "John Doe",
                        "nick_name": "johndoe",
                        "email": "john@example.com",
                        "create_time": "2025-10-28T10:00:00",
                        "update_time": "2025-10-28T10:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }
    )

