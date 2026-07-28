from uuid import UUID

from app.database import db_connection
from app.presentation.controller.customer_controller import CustomerController
from app.presentation.schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

customer_router = APIRouter(prefix="/customers", tags=["Customers"])
controller = CustomerController()


@customer_router.post("/")
def create_customer(request: CustomerCreateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.create_customer(db, request)


@customer_router.get("/")
def get_all_customers(db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_all_customers(db)


@customer_router.get("/{customer_id}")
def get_customer(customer_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.get_customer_by_id(db, customer_id)


@customer_router.patch("/{customer_id}")
def update_customer(customer_id: UUID, request: CustomerUpdateRequest, db: Session = Depends(db_connection)): # noqa: B008
    return controller.update_customer(db, customer_id, request)


@customer_router.delete("/{customer_id}")
def delete_customer(customer_id: UUID, db: Session = Depends(db_connection)): # noqa: B008
    return controller.delete_customer(db, customer_id)
