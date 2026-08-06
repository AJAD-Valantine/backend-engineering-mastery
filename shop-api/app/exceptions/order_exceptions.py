from fastapi import status

from app.exceptions.base_exception import ShopException


class CartIsEmpty(ShopException):
    def __init__(self, message: str = "Cart is empty"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
    
class OrderNotFound(ShopException):
     def __init__(self, message: str = "Order not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)