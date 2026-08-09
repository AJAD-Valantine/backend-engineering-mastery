from fastapi import status

from app.exceptions.base import ShopException


class UserNotFound(ShopException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class EmailAlreadyExits(ShopException):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
class InvalidCredentials(ShopException):
    def __init__(self, message: str = "Incorrect email or password"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)