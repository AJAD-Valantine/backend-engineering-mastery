from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.presentation.controller.payment_controller import PaymentController
from app.presentation.schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

payment_router = APIRouter(tags=["Payments"])
controller = PaymentController()


# ✅ Standard User Route (Paying for an order)
@payment_router.post("/payments", status_code=201)
def add_payment(
    request: PaymentCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    # NOTE: Inside your controller, you MUST verify that the order being 
    # paid for actually belongs to current_user.user_id!
    return controller.add_payment(db, request, current_user)


# ✅ Standard User Route
@payment_router.get("/payments/{payment_id}")
def get_payment(
    payment_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.get_payment_by_id(db, payment_id, current_user)


# ✅ Standard User Route
@payment_router.get("/orders/{order_id}/payment")
def get_payment_by_order(
    order_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.get_payment_by_order(db, order_id, current_user)


# 🚨 Admin Only
@payment_router.put("/payments/{payment_id}/status")
def update_payment_status(
    payment_id: int, 
    request: PaymentUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.update_payment_status(db, payment_id, request)