from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.core.dependencies import db_connection, get_current_user
from app.schemas.product import (
    PaginatedProductResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from app.services.product import ProductService

product_router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService()


# RBAC pending
@product_router.post(
    path="/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[Depends(get_current_user)],
)
def create_product(
    request: ProductCreateRequest, 
    db: Session = Depends(db_connection),
):
    return product_service.add_product(db, request)


# Public Route
@product_router.get(
    path="/",
    response_model=PaginatedProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all products",
)
def get_all_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(db_connection)
): 
    return product_service.get_all_products(
        db=db,
        page=page,
        size=size)


# Public Route
@product_router.get(
    path="/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a product",
)
def get_product(
        product_id: int,
        db: Session = Depends(db_connection)
):
    return product_service.get_product_by_id(db, product_id)


# RBAC pending
@product_router.patch(
    path="/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
    dependencies=[Depends(get_current_user)],
)
def update_product(
    product_id: int, 
    request: ProductUpdateRequest, 
    db: Session = Depends(db_connection),
):
    return product_service.update_product(
        db=db,
        product_id=product_id,
        request=request
    )


# RBAC pending
@product_router.delete(
    path="/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    dependencies=[Depends(get_current_user)],
)
def delete_product(
    product_id: int, 
    db: Session = Depends(db_connection),
):
    return product_service.remove_product(db, product_id)