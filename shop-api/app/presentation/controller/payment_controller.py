from app.exceptions.base_exception import ShopException
from app.exceptions.order_exceptions import OrderNotFound
from app.exceptions.payment_exceptions import (
    InvalidPaymentAmount,
    PaymentAlreadyExists,
    PaymentNotFound,
)
from app.presentation.schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
)
from app.services.payment_service import PaymentService
from fastapi import HTTPException, status


class PaymentController:
    
    def __init__(self):
        self.payment_service = PaymentService()

    def add_payment(self, db, request: PaymentCreateRequest, current_user):
        try:
            return self.payment_service.add_payment(db, request, current_user)
            
        except (PaymentAlreadyExists, InvalidPaymentAmount) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except OrderNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_payment_by_id(self, db, payment_id: int, current_user):
        try:
            return self.payment_service.get_payment_by_id(db, payment_id, current_user)
        except (PaymentNotFound, OrderNotFound) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_payment_by_order(self, db, order_id: int, current_user):
        try:
            return self.payment_service.get_payment_by_order_id(db, order_id, current_user)
        except (PaymentNotFound, OrderNotFound) as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update_payment_status(self, db, payment_id: int, request: PaymentUpdateRequest):
        try:
            return self.payment_service.update_payment_status(db, payment_id, request.payment_status)
            
        except PaymentNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))