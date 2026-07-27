from uuid import UUID
from app.presentation.schemas.response_model import success_response, error_response
from app.services.customer_service import CustomerService
from app.exceptions.customer_exceptions import CustomerNotFound, EmailAlreadyExits
from app.presentation.schemas.customer_schema import CustomerResponse


class CustomerController:
    def __init__(self) -> None:
        self.customer_service = CustomerService()

    def create_customer(self, db, request):

        try:
            raw_customer = self.customer_service.add_customer(db, request)

            customer = CustomerResponse.model_validate(raw_customer).model_dump()
            return success_response(customer, "customer created successfully")

        except EmailAlreadyExits as e:
            return error_response(str(e), 400)

        except Exception as e:
            return error_response(str(e), 500)

    def get_all_customers(self, db):

        try:
            raw_customers = self.customer_service.get_all_customers(db)
            customers = [
                CustomerResponse.model_validate(customer).model_dump()
                for customer in raw_customers
            ]

            if customers:
                return success_response(customers, "fetched all customers")
            else:
                return error_response("no customers available", 404)

        except Exception as e:
            return error_response(str(e), 500)

    def get_customer_by_id(self, db, customer_id: UUID):

        try:
            raw_customer = self.customer_service.get_customer_by_id(db, customer_id)
            customer = CustomerResponse.model_validate(raw_customer).model_dump()
            return success_response(customer, "fetched customer")

        except CustomerNotFound as e:
            return error_response(str(e), 404)

        except Exception as e:
            return error_response(str(e), 500)

    def update_customer(self, db, customer_id, request):

        try:
            raw_customer = self.customer_service.update_customer(
                db, customer_id, request
            )
            customer = CustomerResponse.model_validate(raw_customer).model_dump()
            return success_response(customer, "customer updated")

        except CustomerNotFound as e:
            return error_response(str(e), 404)

        except Exception as e:
            return error_response(str(e), 500)

    def delete_customer(self, db, customer_id):

        try:
            raw_customer = self.customer_service.remove_customer(db, customer_id)
            customer = CustomerResponse.model_validate(raw_customer).model_dump()
            return success_response(customer, "customer deleted")

        except CustomerNotFound as e:
            return error_response(str(e), 404)

        except Exception as e:
            return error_response(str(e), 500)
