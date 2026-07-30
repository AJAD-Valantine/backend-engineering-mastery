from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.presentation.controller.product_controller import ProductController
from app.presentation.schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

product_router = APIRouter(prefix="/products", tags=["Products"])
controller = ProductController()


# 🚨 Admin Only (RBAC pending)
@product_router.post("/")
def create_product(
    request: ProductCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.create_product(db, request)


# 🌍 Public Route (No token required)
@product_router.get("/")
def get_all_products(db: Session = Depends(db_connection)): 
    return controller.get_all_products(db)


# 🌍 Public Route (No token required)
@product_router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(db_connection)): 
    return controller.get_product_by_id(db, product_id)


# 🚨 Admin Only (RBAC pending)
@product_router.patch("/{product_id}")
def update_product(
    product_id: int, 
    request: ProductUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.update_product(db, product_id, request)


# 🚨 Admin Only (RBAC pending)
@product_router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.remove_product(db, product_id)