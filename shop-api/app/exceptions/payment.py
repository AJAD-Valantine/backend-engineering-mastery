from fastapi import status

from app.exceptions.base import ShopException


class PaymentNotFound(ShopException):
    def __init__(self, message: str = "Payment not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class PaymentAlreadyExists(ShopException):
    def __init__(self, message: str = "Payment already exists"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class InvalidPaymentAmount(ShopException):
    def __init__(self, message: str = "Invalid payment amount"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)