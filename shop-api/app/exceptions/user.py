from fastapi import status

from app.exceptions.base import ShopException


class UserNotFound(ShopException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class EmailAlreadyExits(ShopException):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class InvalidCredentials(ShopException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionDenied(ShopException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)

class IncorrectPassword(ShopException):
    def __init__(self, message: str = "Current password is incorrect"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)
