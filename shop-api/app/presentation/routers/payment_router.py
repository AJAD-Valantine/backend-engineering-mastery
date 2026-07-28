from app.database import db_connection
from app.presentation.controller.payment_controller import PaymentController
from app.presentation.schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

payment_router = APIRouter(tags=["Payments"])
controller = PaymentController()


@payment_router.post("/payments", status_code=201)
def add_payment(request: PaymentCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.add_payment(db, request)


@payment_router.get("/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_payment_by_id(db, payment_id)


@payment_router.get("/orders/{order_id}/payment")
def get_payment_by_order(order_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_payment_by_order(db, order_id)


@payment_router.put("/payments/{payment_id}/status")
def update_payment_status(payment_id: int, request: PaymentUpdateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.update_payment_status(db, payment_id, request)