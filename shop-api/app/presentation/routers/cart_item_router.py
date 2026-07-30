from uuid import UUID

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.presentation.controller.cart_item_controller import CartItemController
from app.presentation.schemas.cart_item_schema import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

cart_item_router = APIRouter(tags=["Cart Items"])
controller = CartItemController()

# ✅ Standard User Route
@cart_item_router.post("/cart")
def add_cart_item(
    request: CartItemCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.add_cart_item(db, request)


# ✅ Standard User Route
@cart_item_router.get("/cart/me")
def view_cart(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    # Safely pull the ID directly from the authenticated token
    safe_uuid = UUID(str(current_user.user_id))
    return controller.view_cart(db, safe_uuid)


# ✅ Standard User Route
@cart_item_router.get("/item/{cart_item_id}")
def get_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.get_cart_item_by_id(db, cart_item_id)

# ✅ Standard User Route
@cart_item_router.patch("/cart/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    request: CartItemUpdateRequest,
    db: Session = Depends(db_connection), 
    current_user: Users = Depends(get_current_user)
):
    return controller.update_cart_item(db, cart_item_id, request)

# ✅ Standard User Route
@cart_item_router.delete("/cart/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.remove_cart_item(db, cart_item_id)