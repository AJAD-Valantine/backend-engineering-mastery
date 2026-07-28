import uuid

from app.exceptions.customer_exceptions import CustomerNotFound, EmailAlreadyExits
from app.models.customer_model import Customers
from app.presentation.schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
)
from app.repository.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self) -> None:
        self.customer_repository = CustomerRepository()

    def add_customer(self, db, customer: CustomerCreateRequest):

        if (
            self.customer_repository.read_customer_by_email(db, customer.email)
            is not None
        ):
            raise EmailAlreadyExits("email already exits.")

        customer_id = uuid.uuid4()

        data = Customers(
            customer_id=customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
        )

        return self.customer_repository.create_customer(db, data)

    def get_all_customers(self, db):

        return self.customer_repository.read_all_customers(db)

    def get_customer_by_id(self, db, customer_id):

        customer = self.customer_repository.read_customer_by_id(db, customer_id)

        if customer is None:
            raise CustomerNotFound("customer not found")

        return customer

    def update_customer(self, db, customer_id, request: CustomerUpdateRequest):

        customer = self.customer_repository.read_customer_by_id(db, customer_id)

        if customer is None:
            raise CustomerNotFound("customer not found")

        return self.customer_repository.update_customer(db, customer_id, request)

    def remove_customer(self, db, customer_id):

        customer = self.customer_repository.read_customer_by_id(db, customer_id)

        if customer is None:
            raise CustomerNotFound("customer not found")

        return self.customer_repository.delete_customer(db, customer_id)
