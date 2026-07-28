from uuid import UUID

from app.database import db_connection
from app.presentation.controller.cart_item_controller import CartItemController
from app.presentation.schemas.cart_item_schema import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

cart_item_router = APIRouter(tags=["Cart Items"])
controller = CartItemController()


@cart_item_router.post("/cart")
def add_cart_item(request: CartItemCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.add_cart_item(db, request)


@cart_item_router.get("/customers/{customer_id}/cart")
def view_cart(customer_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.view_cart(db, customer_id)


@cart_item_router.get("/item/{cart_item_id}")
def get_cart_item(cart_item_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_cart_item_by_id(db, cart_item_id)


@cart_item_router.patch("/cart/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    request: CartItemUpdateRequest,
    db: Session = Depends(db_connection), # noqa: B008
):
    return controller.update_cart_item(db, cart_item_id, request)


@cart_item_router.delete("/cart/{cart_item_id}")
def remove_cart_item(cart_item_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.remove_cart_item(db, cart_item_id)
