from decimal import Decimal
from uuid import UUID

from app.exceptions.order_exceptions import CartIsEmpty, OrderNotFound
from app.models.order_item_model import OrderItems
from app.models.order_model import Orders
from app.repository.order_repository import OrderRepository
from app.services.cart_item_service import CartItemService
from app.services.product_service import ProductService
from sqlalchemy.orm import Session


class OrderService:
    
    def __init__(self):
        self.order_repository = OrderRepository()
        self.cart_service = CartItemService()
        self.product_service = ProductService()

    
    def checkout(self, db: Session, user_id: UUID):
        
        cart_items = self.cart_service.view_cart(db, user_id)
        
        if not cart_items:
            raise CartIsEmpty("Cannot checkout an empty cart")

        new_order = Orders(
            user_id=user_id,
            total_amount=0.0
        )
        new_order = self.order_repository.create_order(db, new_order)

        total_order_amount = Decimal("0.0")
        order_items_list = []

        for cart_item in cart_items:
            
            product = self.product_service.get_product_by_id(db, cart_item.product_id)
            
            sub_total = cart_item.quantity * product.price
            total_order_amount += sub_total
            
            new_order_item = OrderItems(
                order_id=new_order.id, 
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                sub_total=sub_total
            )
            order_items_list.append(new_order_item)
            
            product.stock_quantity -= cart_item.quantity
            
            db.delete(cart_item)

        self.order_repository.create_order_items(db, order_items_list)
        
        new_order.total_amount = total_order_amount
        
        db.commit()
        db.refresh(new_order)
        
        return new_order

    def get_all_orders(self, db: Session):
        return self.order_repository.read_all_orders(db)
    
    def get_order_by_id(self, db: Session, order_id: int, current_user):
        order = self.order_repository.read_order_by_id(db, order_id)
        if not order:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        if order.user_id != current_user.user_id and current_user.role != "admin":
            raise OrderNotFound(f"Order with ID {order_id} not found")  
        
        return order

    def get_user_orders(self, db: Session, user_id: UUID):
        return self.order_repository.read_order_by_user_id(db, user_id)
    
    def update_order_status(self, db: Session, order_id: int, status_update: str):
        
        order = self.order_repository.update_status(db, order_id, status_update)
        if not order:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        return order