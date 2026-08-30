from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import CurrentUser, get_cart_service
from app.schemas.cart_item import (
    CartItemCreateRequest,
    CartItemResponse,
    CartItemUpdateRequest,
)
from app.services.cart_item import CartService

from ..models.cart_item import CartItems

cart_item_router = APIRouter(tags=["Cart"])

# Standard User Route
@cart_item_router.post(
    path="/my-cart/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an item to the cart",
)
def add_cart_item(
    request: CartItemCreateRequest,
    current_user: CurrentUser,
    cart_service : CartService = Depends(get_cart_service)
):
    return cart_service.add_to_cart(
        user_id=current_user.user_id,
        request=request
    )

# Standard User Route
@cart_item_router.get(
    path="/my-cart",
    response_model=list[CartItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all items in my cart",
)
def view_cart(
    current_user: CurrentUser,
    cart_service : CartService = Depends(get_cart_service)
):
    return cart_service.view_cart(current_user.user_id)

# Standard User Route
@cart_item_router.get(
    path="/my-cart/items/{item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific cart item",
)
def get_cart_item(
    item_id: int,
    current_user: CurrentUser,
    cart_service : CartService = Depends(get_cart_service)
) -> CartItems:
    return cart_service.view_cart_item_by_id(
        user_id=current_user.user_id,
        item_id=item_id,
    )

# Standard User Route
@cart_item_router.patch(
    path="/my-cart/items/{item_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the quantity of a cart item",
)
def update_cart_item(
    item_id: int,
    request: CartItemUpdateRequest,
    current_user: CurrentUser,
    cart_service : CartService = Depends(get_cart_service)
) -> CartItems:
    return cart_service.update_quantity(
        user_id=current_user.user_id,
        item_id=item_id,
        request=request
    )

# Standard User Route
@cart_item_router.delete(
    path="/my-cart/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item from my cart",
)
def remove_cart_item(
    item_id: int,
    current_user: CurrentUser,
    cart_service : CartService = Depends(get_cart_service)
) -> None:
    cart_service.remove_cart_item(
        user_id=current_user.user_id,
        item_id=item_id,
    )
