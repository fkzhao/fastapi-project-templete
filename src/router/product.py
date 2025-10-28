from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime

from schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
)
from schemas.base import MessageResponse

router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
async def create_product(product_data: ProductCreateRequest):
    """
    Create a new product with the provided data.
    """
    # TODO: Implement actual database creation logic
    return ProductResponse(
        id=1,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=product_data.category,
        create_time=datetime.now(),
        update_time=datetime.now()
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID"
)
async def get_product(product_id: int):
    """
    Retrieve a product by its ID.
    """
    # TODO: Implement actual database lookup
    if product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return ProductResponse(
        id=product_id,
        name="Laptop",
        description="High-performance laptop",
        price=999.99,
        stock=50,
        category="Electronics",
        create_time=datetime.now(),
        update_time=datetime.now()
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product"
)
async def update_product(product_id: int, product_data: ProductUpdateRequest):
    """
    Update an existing product with the provided data.
    Only provided fields will be updated.
    """
    # TODO: Implement actual database update logic
    return ProductResponse(
        id=product_id,
        name=product_data.name or "Laptop",
        description=product_data.description or "High-performance laptop",
        price=product_data.price or 999.99,
        stock=product_data.stock or 50,
        category=product_data.category or "Electronics",
        create_time=datetime.now(),
        update_time=datetime.now()
    )


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    summary="Delete product"
)
async def delete_product(product_id: int):
    """
    Delete a product by its ID.
    """
    # TODO: Implement actual database deletion logic
    return MessageResponse(
        message=f"Product {product_id} deleted successfully",
        code=200
    )


@router.get(
    "/",
    response_model=ProductListResponse,
    summary="Get product list"
)
async def get_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    category: str = Query(default=None, description="Filter by category")
):
    """
    Get a paginated list of products.

    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 10, max: 100)
    - **category**: Optional category filter
    """
    # TODO: Implement actual database query with pagination
    products = [
        ProductResponse(
            id=1,
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            stock=50,
            category="Electronics",
            create_time=datetime.now(),
            update_time=datetime.now()
        )
    ]

    return ProductListResponse(
        items=products,
        total=1,
        page=page,
        page_size=page_size
    )

