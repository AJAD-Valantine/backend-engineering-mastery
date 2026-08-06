from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.schemas.cart_item_schema import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
)
from app.services.cart_item_service import CartItemService

cart_item_router = APIRouter(tags=["Cart Items"])
cart_item_service = CartItemService()

# ✅ Standard User Route
@cart_item_router.post("/cart")
def add_cart_item(
    request: CartItemCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.add_to_cart(db, current_user.user_id, request)  


# ✅ Standard User Route
@cart_item_router.get("/cart/me")
def view_cart(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.view_cart(db, current_user.user_id)  


# ✅ Standard User Route
@cart_item_router.get("/item/{cart_item_id}")
def get_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.view_cart_item_by_id(db, cart_item_id)

# ✅ Standard User Route
@cart_item_router.patch("/cart/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    request: CartItemUpdateRequest,
    db: Session = Depends(db_connection), 
    current_user: Users = Depends(get_current_user)
):
    return cart_item_service.update_quantity(db, cart_item_id, request)

# ✅ Standard User Route
@cart_item_router.delete("/cart/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.remove_cart_item(db, cart_item_id)