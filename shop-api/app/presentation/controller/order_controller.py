from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.order_exceptions import CartIsEmpty, OrderNotFound
from app.presentation.schemas.order_schema import OrderResponse, OrderUpdateRequest
from app.presentation.schemas.response_model import error_response, success_response
from app.services.order_service import OrderService


class OrderController:

    def __init__(self):
        self.order_service = OrderService()

    def checkout(self, db, user_id: UUID):
        
        try:
            order = self.order_service.checkout(db, user_id)
            response_data = OrderResponse.model_validate(order).model_dump()
            return success_response(data=response_data, message="Order placed successfully")
            
        except CartIsEmpty as e:
            return error_response(str(e), 400)
        except ShopException as e:
            return error_response(str(e), 500)


    def get_order_by_id(self, db, order_id: int):

        try:
            order = self.order_service.get_order_by_id(db, order_id)
            response_data = OrderResponse.model_validate(order).model_dump()
            return success_response(data=response_data, message="Order fetched")
        
        except OrderNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)


    def get_all_orders(self, db):

        try:
            orders = self.order_service.get_all_orders(db)
            response_orders = []
            
            for order in orders:
                response_data = OrderResponse.model_validate(order).model_dump()
                response_orders.append(response_data)

            return success_response(data=response_orders, message="Orders fetched")
            
        except ShopException as e:
            return error_response(str(e), 500)


    def get_user_orders(self, db, user_id: UUID):

        try:
            orders = self.order_service.get_user_orders(db, user_id)
            response_orders = []

            for order in orders:
                response_data = OrderResponse.model_validate(order).model_dump()
                response_orders.append(response_data)

            return success_response(data=response_orders, message="Orders fetched")
            
        except ShopException as e:
            return error_response(str(e), 500)


    def update_order_status(self, db, order_id: int, request: OrderUpdateRequest):
        try:
            order = self.order_service.update_order_status(db, order_id, request.status)
            response_data = OrderResponse.model_validate(order).model_dump()
            return success_response(data=response_data, message="Order status updated")

        except OrderNotFound as e:
            return error_response(str(e), 404)
        except ShopException as e:
            return error_response(str(e), 500)