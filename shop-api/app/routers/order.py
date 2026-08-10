from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user import Users
from app.schemas.order import OrderUpdateRequest, PaginatedOrderResponse, OrderResponse
from app.services.order import OrderService

order_router = APIRouter(prefix="/orders", tags=["Orders"])
order_service = OrderService()


# User Route
@order_router.post(
    path="/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
def create_order(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.checkout(
        db=db,
        user_id=current_user.user_id
    )


# RBAC pending
@order_router.get(
    path="/",
    response_model=PaginatedOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all orders",
    dependencies=[Depends(get_current_user)],
)
def get_orders(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(db_connection),
): 
    return order_service.get_all_orders(
        db=db,
        page=page,
        size=size
    )


# User Route
@order_router.get(
    path="me/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a user order",
)
def get_order(
    order_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.get_order_by_id(
        db=db,
        order_id=order_id,
        user_id=current_user
    )


# User Route
@order_router.get(
    path="/my-orders",
    response_model=PaginatedOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all user orders",
)
def get_user_orders(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.get_user_orders(
        db=db,
        user_id=current_user.user_id
    )


# RBAC pending
@order_router.put(
    path="/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user order",
    dependencies=[Depends(get_current_user)],
)
def update_order_status(
    order_id: int, 
    request: OrderUpdateRequest, 
    db: Session = Depends(db_connection),
):
    return order_service.update_order_status(
        db=db,
        order_id=order_id,
        status_update=request.status
    )