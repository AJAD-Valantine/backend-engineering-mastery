from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions.order import CartIsEmpty, OrderNotFound
from app.models.order_item import OrderItems
from app.models.order import Orders
from app.repository.cart_item import CartItemRepository
from app.repository.order import OrderRepository
from app.services.cart_item import CartItemService
from app.services.product import ProductService


class OrderService:
    
    def __init__(self):
        self.order_repository = OrderRepository()
        self.cart_service = CartItemService()
        self.cart_repository = CartItemRepository()
        self.product_service = ProductService()

    
    def checkout(
            self,
            db: Session,
            user_id: UUID
    ):
        
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
            
            self.cart_repository.remove_cart_item_for_checkout(db, cart_item)

        self.order_repository.create_order_items(db, order_items_list)
        
        new_order.total_amount = total_order_amount
        
        db.commit()
        db.refresh(new_order)
        
        return new_order

    def get_all_orders(
            self,
            db: Session,
            page: int = 1,
            size: int = 10
    ):

        skip = (page - 1) * size
        total_items, orders = self.order_repository.read_all_orders(db, skip=skip, limit=size)
        
        return {
            "total_items": total_items,
            "page": page,
            "size": size,
            "data": orders
        }
    
    def get_order_by_id(
            self,
            db: Session,
            order_id: int,
            user_id: UUID
    ):
        order = self.order_repository.read_order_by_id(db, order_id)

        if order is None or order.user_id != user_id:
            raise OrderNotFound(f"Order with ID {order_id} not found")  
        
        return order

    def get_user_orders(
            self,
            db: Session,
            user_id: UUID
    ):
        return self.order_repository.read_order_by_user_id(db, user_id)
    
    def update_order_status(
            self,
            db: Session,
            order_id: int,
            status_update: str
    ):

        order = self.order_repository.read_order_by_id(db, order_id)

        if order is None:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        
        order = self.order_repository.update_status(db, order_id, status_update)

        return order