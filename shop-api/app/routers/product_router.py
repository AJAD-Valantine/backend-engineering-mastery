from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.schemas.product_schema import (
    PaginatedProductResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.services.product_service import ProductService

product_router = APIRouter(prefix="/products", tags=["Products"])
product_service = ProductService()


# 🚨 Admin Only (RBAC pending)
@product_router.post("/")
def create_product(
    request: ProductCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return product_service.add_product(db, request)


# 🌍 Public Route (No token required)
@product_router.get("/", response_model=PaginatedProductResponse)
def get_all_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(db_connection)
): 
    return product_service.get_all_products(db, page=page, size=size)


# 🌍 Public Route (No token required)
@product_router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(db_connection)): 
    return product_service.get_product_by_id(db, product_id)


# 🚨 Admin Only (RBAC pending)
@product_router.patch("/{product_id}")
def update_product(
    product_id: int, 
    request: ProductUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return product_service.update_product(db, product_id, request)


# 🚨 Admin Only (RBAC pending)
@product_router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return product_service.remove_product(db, product_id)