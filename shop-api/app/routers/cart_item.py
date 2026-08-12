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
from app.services.cart_item import CartService

cart_item_router = APIRouter(tags=["Cart"])
cart_service = CartService()

@cart_item_router.post(
    path="/my-cart/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an item to the cart",
)
def add_cart_item(
    request: CartItemCreateRequest,
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return cart_service.add_to_cart(
        db=db,
        user_id=current_user.user_id,
        request=request
    )


@cart_item_router.get(
    path="/my-cart",
    response_model=list[CartItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all items in my cart",
)
def view_cart(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return cart_service.view_cart(
        db=db,
        user_id=current_user.user_id
    )


@cart_item_router.get(
    path="/my-cart/items/{item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific cart item",
)
def get_cart_item(
    item_id: int,
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return cart_service.view_cart_item_by_id(
        db=db,
        user_id=current_user.user_id,
        item_id=item_id,
    )


@cart_item_router.patch(
    path="/my-cart/items/{item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the quantity of a cart item",
)
def update_cart_item(
    item_id: int,
    request: CartItemUpdateRequest,
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return cart_service.update_quantity(
        db=db,
        user_id=current_user.user_id,
        item_id=item_id,
        request=request
    )


@cart_item_router.delete(
    path="/my-cart/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item from my cart",
)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
):
    return cart_service.remove_cart_item(
        db=db,
        user_id=current_user.user_id,
        item_id=item_id,
    )