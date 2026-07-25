from uuid import UUID
from sqlalchemy.orm import Session
from app.models.customer_model import Customers
from app.presentation.schemas.customer_schema import CustomerUpdateRequest


class CustomerRepository:
    def create_customer(self, db: Session, customer: Customers):

        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def read_all_customers(self, db: Session):

        return db.query(Customers).all()

    def read_customer_by_id(self, db: Session, customer_id: UUID):

        return db.query(Customers).filter(Customers.customer_id == customer_id).first()

    def read_customer_by_email(self, db: Session, email: str):

        return db.query(Customers).filter(Customers.email == email).first()

    def update_customer(
        self, db: Session, customer_id: UUID, request: CustomerUpdateRequest
    ):

        customer = (
            db.query(Customers).filter(Customers.customer_id == customer_id).first()
        )

        update_data = request.model_dump(exclude_unset=True)

        if customer is not None:
            for key, value in update_data.items():
                setattr(customer, key, value)

            db.commit()
            db.refresh(customer)
            return customer

    def delete_customer(self, db: Session, customer_id):

        customer = (
            db.query(Customers).filter(Customers.customer_id == customer_id).first()
        )

        db.delete(customer)
        db.commit()

        return customer
