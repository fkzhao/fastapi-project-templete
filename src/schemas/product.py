"""
Product-related Pydantic schemas for request/response validation.
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from .base import BaseResponse, TimestampSchema


# ============ Request Schemas ============

class ProductCreateRequest(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Product price")
    stock: int = Field(default=0, ge=0, description="Stock quantity")
    category: Optional[str] = Field(None, max_length=50, description="Product category")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "stock": 50,
                "category": "Electronics"
            }
        }
    )


class ProductUpdateRequest(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Product price")
    stock: Optional[int] = Field(None, ge=0, description="Stock quantity")
    category: Optional[str] = Field(None, max_length=50, description="Product category")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 899.99,
                "stock": 45
            }
        }
    )


# ============ Response Schemas ============

class ProductResponse(BaseResponse, TimestampSchema):
    """Schema for product response."""
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., description="Product price")
    stock: int = Field(..., description="Stock quantity")
    category: Optional[str] = Field(None, description="Product category")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "stock": 50,
                "category": "Electronics",
                "create_time": "2025-10-28T10:00:00",
                "update_time": "2025-10-28T10:00:00"
            }
        }
    )


class ProductBriefResponse(BaseModel):
    """Brief product info (for list views)."""
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: Decimal = Field(..., description="Product price")
    stock: int = Field(..., description="Stock quantity")

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Response for product list with pagination."""
    items: List[ProductResponse] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")

