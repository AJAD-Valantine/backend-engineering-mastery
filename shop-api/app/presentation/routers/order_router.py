from uuid import UUID

from app.database import db_connection
from app.presentation.controller.order_controller import OrderController
from app.presentation.schemas.order_schema import OrderUpdateRequest
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

order_router = APIRouter(tags=["Orders"])
controller = OrderController()


@order_router.post("/orders/user/{user_id}", status_code=201)
def create_order(user_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.checkout(db, user_id)

@order_router.get("/orders")
def get_orders(db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_all_orders(db)

@order_router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_order_by_id(db, order_id)

@order_router.get("/users/{user_id}/orders")
def get_user_orders(user_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_user_orders(db, user_id)

@order_router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, request: OrderUpdateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.update_order_status(db, order_id, request)