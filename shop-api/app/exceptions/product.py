from fastapi import status

from app.exceptions.base import ShopException


class ProductNotFound(ShopException):
    def __init__(self, message: str = "Product not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)
