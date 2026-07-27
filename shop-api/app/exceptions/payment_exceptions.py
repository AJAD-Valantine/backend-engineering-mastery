from app.exceptions.base_exception import ShopException


class PaymentNotFound(ShopException):
    pass

class PaymentAlreadyExists(ShopException):
    pass

class InvalidPaymentAmount(ShopException):
    pass