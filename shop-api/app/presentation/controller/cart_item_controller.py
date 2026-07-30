from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.cart_item_exceptions import (
    CartItemNotFound,
    NotEnoughStockAvailable,
)
from app.presentation.schemas.cart_item_schema import CartItemResponse
from app.presentation.schemas.response_model import error_response, success_response
from app.services.cart_item_service import CartItemService


class CartItemController:
    def __init__(self):
        self.cart_item_service = CartItemService()

    def add_cart_item(self, db, request):

        try:
            cart_item = self.cart_item_service.add_to_cart(db, request)

            response_data = CartItemResponse.model_validate(cart_item).model_dump()
            return success_response(response_data, "Cart item added successfully")

        except NotEnoughStockAvailable as e:
            return error_response(str(e), 400)

        except ShopException as e:
            return error_response(str(e), 500)

    def view_cart(self, db, user_id: UUID):

        try:
            cart_items = self.cart_item_service.view_cart(db, user_id)

            response_data = [
                CartItemResponse.model_validate(item).model_dump()
                for item in cart_items
            ]
            return success_response(response_data, "Cart items fetched successfully")

        except ShopException as e:
            return error_response(str(e), 500)

    def get_cart_item_by_id(self, db, cart_item_id):

        try:
            cart_item = self.cart_item_service.view_cart_item_by_id(db, cart_item_id)

            response_data = CartItemResponse.model_validate(cart_item).model_dump()
            return success_response(response_data, "Cart item fetched successfully")

        except CartItemNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def update_cart_item(self, db, cart_item_id, request):

        try:
            cart_item = self.cart_item_service.update_quantity(
                db, cart_item_id, request
            )

            response_data = CartItemResponse.model_validate(cart_item).model_dump()
            return success_response(response_data, "Cart item updated successfully")

        except NotEnoughStockAvailable as e:
            return error_response(str(e), 400)

        except CartItemNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def remove_cart_item(self, db, cart_item_id):

        try:
            self.cart_item_service.remove_cart_item(db, cart_item_id)

            return success_response(None, "Cart item removed successfully")

        except CartItemNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)
