from uuid import UUID

from app.models.cart_item_model import CartItems
from sqlalchemy.orm import Session


class CartItemRepository:

    def create_cart_item(self, db : Session, cart_item : CartItems):

        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

        return cart_item
    
    def read_cart(self, db : Session, user_id : UUID):

        return db.query(CartItems).filter(CartItems.user_id == user_id).all()
    
    def read_cart_item_by_id(self, db : Session, cart_item_id : int):

        return db.query(CartItems).filter(CartItems.cart_id == cart_item_id).first()
    
    def update_quantity(self, db : Session, cart_item_id : int, quantity: int):

        cart_item = self.read_cart_item_by_id(db, cart_item_id)

        if cart_item is not None:

            cart_item.quantity = quantity
        
            db.commit()
            db.refresh(cart_item)

        return cart_item
    
    def delete_cart_item(self, db : Session, cart_item_id : int):

        cart_item = self.read_cart_item_by_id(db, cart_item_id)

        if cart_item is not None:

            db.delete(cart_item)
            db.commit()

        return cart_item