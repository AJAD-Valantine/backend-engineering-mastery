from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user import Users
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentUpdateRequest,
    PaymentResponse,
)
from app.services.payment import PaymentService

payment_router = APIRouter(tags=["Payments"])
payment_service = PaymentService()


# User Route
@payment_router.post(
    path="/payments",
    status_code=status.HTTP_201_CREATED,
    response_model=PaymentResponse,
    summary="Create a new payment",
)
def add_payment(
    request: PaymentCreateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return payment_service.add_payment(
        db=db,
        request=request,
        current_user=current_user
    )


# User Route
@payment_router.get(
    path="/payments/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a payment method by payment id",
)
def get_payment(
    payment_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return payment_service.get_payment_by_id(
        db=db,
        payment_id=payment_id,
        current_user=current_user
    )


# User Route
@payment_router.get(
    path="/orders/{order_id}/payment",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a payment method by order_id",
)
def get_payment_by_order(
    order_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return payment_service.get_payment_by_order_id(
        db=db,
        order_id=order_id,
        current_user=current_user
    )


# RBAC Pending
@payment_router.put(
    path="/payments/{payment_id}/status",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a payment status",
    dependencies=[Depends(get_current_user)],
)
def update_payment_status(
    payment_id: int, 
    request: PaymentUpdateRequest, 
    db: Session = Depends(db_connection),
): 
    return payment_service.update_payment_status(
        db=db,
        payment_id=payment_id,
        status=request.payment_status
    )