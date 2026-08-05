from uuid import UUID

from app.core.dependencies import db_connection, get_current_user
from app.models.user_model import Users
from app.presentation.controller.order_controller import OrderController
from app.presentation.schemas.order_schema import OrderUpdateRequest
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

order_router = APIRouter(prefix="/orders", tags=["Orders"])
controller = OrderController()


# ✅ Standard User Route
@order_router.post("/checkout", status_code=201)
def create_order(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    safe_uuid = UUID(str(current_user.user_id))
    return controller.checkout(db, safe_uuid)


# 🚨 Admin Only (RBAC pending)
@order_router.get("/")
def get_orders(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.get_all_orders(db)


# ✅ Standard User Route
@order_router.get("/{order_id}")
def get_order(
    order_id: int, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.get_order_by_id(db, order_id, current_user)


# ✅ Standard User Route
@order_router.get("/me")
def get_user_orders(
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    safe_uuid = UUID(str(current_user.user_id))
    return controller.get_user_orders(db, safe_uuid)


# 🚨 Admin Only (RBAC pending)
@order_router.put("/{order_id}/status")
def update_order_status(
    order_id: int, 
    request: OrderUpdateRequest, 
    db: Session = Depends(db_connection),
    current_user: Users = Depends(get_current_user)
): 
    return controller.update_order_status(db, order_id, request)