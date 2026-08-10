from sqlalchemy.orm import Session

from app.models.payment import Payments


class PaymentRepository:

    def create_payment(
            self,
            db: Session,
            payment: Payments
    ):
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    def read_payment_by_id(
            self,
            db: Session,
            payment_id: int
    ):
        return db.query(Payments).filter(Payments.id == payment_id).first()

    def read_payment_by_order_id(
            self,
            db: Session,
            order_id: int
    ):
        return db.query(Payments).filter(Payments.order_id == order_id).first()

    def update_payment_status(
            self,
            db: Session,
            payment_id: int,
            status: str
    ):
        payment = self.read_payment_by_id(db, payment_id)
        
        if payment is None:
            return None

        payment.payment_status = status
        db.commit()
        db.refresh(payment)

        return payment