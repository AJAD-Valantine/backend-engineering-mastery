from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.core.dependencies import db_connection, get_current_user
from app.models.user import Users
from app.schemas.cart_item import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
    CartItemResponse,
)
from app.services.cart_item import CartItemService

cart_item_router = APIRouter(tags=["Cart Items"])
cart_item_service = CartItemService()

# User Route
@cart_item_router.post(
    path="/add-to-cart",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new cart item",
)
def add_cart_item(
    request: CartItemCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.add_to_cart(
        db=db,
        user_id=current_user.user_id,
        cart_item=request)


# User Route
@cart_item_router.get(
    path="/my-cart",
    response_model=list[CartItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all my cart items",
)
def view_cart(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.view_cart(
        db=db,
        user_id=current_user.user_id
    )


# User Route
@cart_item_router.get(
    path="my-cart-items/{cart_item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get my cart item",
)
def get_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.view_cart_item_by_id(
        db=db,
        cart_item_id=cart_item_id,
        user_id=current_user.user_id
    )

# User Route
@cart_item_router.patch(
    path="my-cart-items/{cart_item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the quantity of my cart item",
)
def update_cart_item(
    cart_item_id: int,
    request: CartItemUpdateRequest,
    db: Session = Depends(db_connection), 
    current_user: Users = Depends(get_current_user)
):
    return cart_item_service.update_quantity(
        db=db,
        cart_item_id=cart_item_id,
        user_id=current_user.user_id,
        update_cart_item=request
    )

# User Route
@cart_item_router.delete(
    path="my-cart-items/{cart_item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete my cart item",
)
def remove_cart_item(
    cart_item_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return cart_item_service.remove_cart_item(
        db=db,
        cart_item_id=cart_item_id,
        user_id=current_user.user_id
    )