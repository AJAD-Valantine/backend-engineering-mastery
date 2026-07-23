from app.exceptions.base_exception import ShopException

class CartIsEmpty(ShopException):
    pass

class OrderNotFound(ShopException):
    pass