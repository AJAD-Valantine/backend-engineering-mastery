from app.exceptions.base_exception import ShopException


class UserNotFound(ShopException):
    pass

class EmailAlreadyExits(ShopException):
    pass