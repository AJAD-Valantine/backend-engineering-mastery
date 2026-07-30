from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.cart_item_exceptions import (
    CartItemNotFound,
    NotEnoughStockAvailable,
)
from app.services.cart_item_service import CartItemService
from fastapi import HTTPException, status


class CartItemController:

    def __init__(self):
        self.cart_item_service = CartItemService()

    def add_cart_item(self, db, request):
        try:
            return self.cart_item_service.add_to_cart(db, request)

        except NotEnoughStockAvailable as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def view_cart(self, db, user_id: UUID):
        try:
            return self.cart_item_service.view_cart(db, user_id)

        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_cart_item_by_id(self, db, cart_item_id: int):
        try:
            return self.cart_item_service.view_cart_item_by_id(db, cart_item_id)

        except CartItemNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update_cart_item(self, db, cart_item_id: int, request):
        try:
            return self.cart_item_service.update_quantity(db, cart_item_id, request)

        except NotEnoughStockAvailable as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except CartItemNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def remove_cart_item(self, db, cart_item_id: int):
        try:
            return self.cart_item_service.remove_cart_item(db, cart_item_id)

        except CartItemNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))