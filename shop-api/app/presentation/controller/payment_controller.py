from app.exceptions.base_exception import ShopException
from app.exceptions.order_exceptions import OrderNotFound
from app.exceptions.payment_exceptions import (
    InvalidPaymentAmount,
    PaymentAlreadyExists,
    PaymentNotFound,
)
from app.presentation.schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentUpdateRequest,
)
from app.presentation.schemas.response_model import error_response, success_response
from app.services.payment_service import PaymentService


class PaymentController:
    def __init__(self):
        self.payment_service = PaymentService()

    def add_payment(self, db, request: PaymentCreateRequest):
        try:
            payment = self.payment_service.add_payment(db, request)
            response_data = PaymentResponse.model_validate(payment).model_dump()
            
            return success_response(data=response_data, message="Payment created successfully")
            
        except (PaymentAlreadyExists, InvalidPaymentAmount) as e:
            return error_response(str(e), 400)
        except OrderNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)


    def get_payment_by_id(self, db, payment_id: int):
        try:
            payment = self.payment_service.get_payment_by_id(db, payment_id)
            response_data = PaymentResponse.model_validate(payment).model_dump()
            
            return success_response(data=response_data, message="Payment fetched successfully")
            
        except PaymentNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)


    def get_payment_by_order(self, db, order_id: int):
        try:
            payment = self.payment_service.get_payment_by_order_id(db, order_id)
            response_data = PaymentResponse.model_validate(payment).model_dump()
            
            return success_response(data=response_data, message="Payment fetched successfully")
            
        except PaymentNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)


    def update_payment_status(self, db, payment_id: int, request: PaymentUpdateRequest):
        try:
            payment = self.payment_service.update_payment_status(db, payment_id, request.payment_status)
            response_data = PaymentResponse.model_validate(payment).model_dump()
            
            return success_response(data=response_data, message="Payment status updated successfully")
            
        except PaymentNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)