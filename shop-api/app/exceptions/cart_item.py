from fastapi import status

from app.exceptions.base import ShopException


class CartItemNotFound(ShopException):
    def __init__(self, message: str = "Cart item not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class NotEnoughStockAvailable(ShopException):
    def __init__(self, message: str = "Not enough stock available"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)