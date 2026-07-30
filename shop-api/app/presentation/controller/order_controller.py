from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.order_exceptions import CartIsEmpty, OrderNotFound
from app.presentation.schemas.order_schema import OrderUpdateRequest
from app.services.order_service import OrderService
from fastapi import HTTPException, status


class OrderController:
    
    def __init__(self):
        self.order_service = OrderService()

    def checkout(self, db, user_id: UUID):
        try:
            return self.order_service.checkout(db, user_id)
            
        except CartIsEmpty as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_order_by_id(self, db, order_id: int):
        try:
            return self.order_service.get_order_by_id(db, order_id)
        
        except OrderNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_all_orders(self, db):
        try:
            orders = self.order_service.get_all_orders(db)
            if not orders:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no orders available")
            
            return orders
            
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_user_orders(self, db, user_id: UUID):
        try:
            orders = self.order_service.get_user_orders(db, user_id)
            if not orders:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no orders found for this user")
            
            return orders
            
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update_order_status(self, db, order_id: int, request: OrderUpdateRequest):
        try:
            return self.order_service.update_order_status(db, order_id, request.status)

        except OrderNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))