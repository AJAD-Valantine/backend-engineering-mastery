from app.core.dependencies import db_connection
from app.presentation.controller.product_controller import ProductController
from app.presentation.schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

product_router = APIRouter(prefix="/products", tags=["Products"])
controller = ProductController()


@product_router.post("/")
def create_product(request: ProductCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.create_product(db, request)


@product_router.get("/")
def get_all_products(db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_all_products(db)


@product_router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_product_by_id(db, product_id)


@product_router.patch("/{product_id}")
def update_product(product_id: int, request: ProductUpdateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.update_product(db, product_id, request)


@product_router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.remove_product(db, product_id)
