# Import the custom exceptions you just made
from app.exceptions.payment_exceptions import (
    InvalidPaymentAmount,
    PaymentAlreadyExists,
    PaymentNotFound,
)
from app.models.payment_model import Payments
from app.presentation.schemas.payment_schema import PaymentCreateRequest
from app.repository.payment_repository import PaymentRepository
from app.services.order_service import OrderService
from sqlalchemy.orm import Session


class PaymentService:
    def __init__(self):
        self.payment_repository = PaymentRepository()
        self.order_service = OrderService()

    def add_payment(self, db: Session, request: PaymentCreateRequest):
        
        # 1. Verify the order exists (OrderService will raise OrderNotFound if it doesn't)
        order = self.order_service.get_order_by_id(db, request.order_id)

        # 2. Enforce Business Rule: One payment per order
        existing_payment = self.payment_repository.read_payment_by_order_id(db, request.order_id)
        if existing_payment:
            raise PaymentAlreadyExists(f"A payment already exists for Order ID {request.order_id}")

        # 3. Enforce Business Rule: Amount must match exactly
        # We cast both to float to avoid Decimal vs Float mismatch errors
        if float(request.paid_amount) != float(order.total_amount):
            raise InvalidPaymentAmount(
                f"Payment amount ({request.paid_amount}) must match the order total ({order.total_amount})"
            )

        # 4. If all checks pass, build the model and save it
        new_payment = Payments(
            order_id=request.order_id,
            payment_method=request.payment_method,
            paid_amount=request.paid_amount
            # payment_status defaults to "Pending" automatically via the DB model
        )
        
        return self.payment_repository.create_payment(db, new_payment)


    def get_payment_by_id(self, db: Session, payment_id: int):
        payment = self.payment_repository.read_payment_by_id(db, payment_id)
        if not payment:
            raise PaymentNotFound(f"Payment with ID {payment_id} not found")
        return payment


    def get_payment_by_order_id(self, db: Session, order_id: int):
        payment = self.payment_repository.read_payment_by_order_id(db, order_id)
        if not payment:
            raise PaymentNotFound(f"No payment record found for Order ID {order_id}")
        return payment


    def update_payment_status(self, db: Session, payment_id: int, status: str):
        payment = self.payment_repository.update_payment_status(db, payment_id, status)
        if not payment:
            raise PaymentNotFound(f"Payment with ID {payment_id} not found")
        return payment