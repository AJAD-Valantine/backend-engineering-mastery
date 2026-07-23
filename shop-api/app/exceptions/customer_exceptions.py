from app.exceptions.base_exception import ShopException


class CustomerNotFound(ShopException):
    pass

class EmailAlreadyExits(ShopException):
    pass