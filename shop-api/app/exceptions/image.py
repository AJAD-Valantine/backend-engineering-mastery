from starlette import status

from app.exceptions.base import ShopException


class InvalidImageFile(ShopException):
    def __init__(self, message: str = "Invalid image file"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)

class FileTooLarge(ShopException):
    def __init__(self, message: str = "File exceeds maximum allowed size"):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)