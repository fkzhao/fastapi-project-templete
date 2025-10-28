"""
Base schemas for common response patterns.
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class TimestampSchema(BaseModel):
    """Mixin for schemas that include timestamp fields."""
    create_time: datetime = Field(..., description="Creation timestamp")
    update_time: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str = Field(..., description="Response message")
    code: int = Field(default=200, description="Status code")


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool = Field(default=True, description="Whether the request was successful")
    data: Optional[T] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Response message")
    code: int = Field(default=200, description="Status code")

