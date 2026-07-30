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
        
        # STEP 1: Get all cart items of the user
        cart_items = self.cart_service.view_cart(db, user_id)
        
        if not cart_items:
            # Safety check: Prevent checking out an empty cart
            raise CartIsEmpty("Cannot checkout an empty cart")

        # STEP 3: Create an order (header) first to get an ID
        # We start with a total of 0.0, we will update it later.
        new_order = Orders(
            user_id=user_id,
            total_amount=0.0
        )
        new_order = self.order_repository.create_order(db, new_order)

        # Prepare for the Super Loop
        total_order_amount = Decimal("0.0")
        order_items_list = []

        # The Super Loop (Handles Steps 2, 4, 5, and 6 simultaneously)
        for cart_item in cart_items:
            
            # Fetch the product ONCE to save database trips
            product = self.product_service.get_product_by_id(db, cart_item.product_id)
            
            # STEP 2: Calculate the subtotal and add to the running total
            sub_total = cart_item.quantity * product.price
            total_order_amount += sub_total
            
            # STEP 4: Create the order items (line items)
            new_order_item = OrderItems(
                order_id=new_order.id,           # This is why Step 3 had to happen first!
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=product.price,
                sub_total=sub_total
            )
            order_items_list.append(new_order_item)
            
            # STEP 5: Reduce product stock
            product.stock_quantity -= cart_item.quantity
            
            # STEP 6: Clear the user cart
            # Deleting the item from the db session wipes it from the cart table
            db.delete(cart_item)

        # Outside the loop: Save the entire list of line items at once
        self.order_repository.create_order_items(db, order_items_list)
        
        # Update the main order with the final calculated total
        new_order.total_amount = total_order_amount
        
        # Commit EVERYTHING (the stock changes, the cart deletion, the total update)
        db.commit()
        db.refresh(new_order)
        
        return new_order

    def get_all_orders(self, db: Session):
        return self.order_repository.read_all_orders(db)
    
    def get_order_by_id(self, db: Session, order_id: int):
        order = self.order_repository.read_order_by_id(db, order_id)
        if not order:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        return order

    def get_user_orders(self, db: Session, user_id: UUID):
        return self.order_repository.read_order_by_user_id(db, user_id)
    
    def update_order_status(self, db: Session, order_id: int, status_update: str):
        
        order = self.order_repository.update_status(db, order_id, status_update)
        if not order:
            raise OrderNotFound(f"Order with ID {order_id} not found")
        return order