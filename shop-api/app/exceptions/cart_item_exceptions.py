from app.exceptions.base_exception import ShopException


class CartItemNotFound(ShopException):
    pass

class NotEnoughStockAvailable(ShopException):
    pass

