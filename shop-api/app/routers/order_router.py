from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.schemas.order_schema import OrderUpdateRequest
from app.services.order_service import OrderService

order_router = APIRouter(prefix="/orders", tags=["Orders"])
order_service = OrderService()


# ✅ Standard User Route
@order_router.post("/checkout", status_code=201)
def create_order(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.checkout(db, current_user.user_id)


# 🚨 Admin Only (RBAC pending)
@order_router.get("/")
def get_orders(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.get_all_orders(db)


# ✅ Standard User Route
@order_router.get("/{order_id}")
def get_order(
    order_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.get_order_by_id(db, order_id, current_user)


# ✅ Standard User Route
@order_router.get("/me")
def get_user_orders(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.get_user_orders(db, current_user.user_id)


# 🚨 Admin Only (RBAC pending)
@order_router.put("/{order_id}/status")
def update_order_status(
    order_id: int, 
    request: OrderUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return order_service.update_order_status(db, order_id, request.status)