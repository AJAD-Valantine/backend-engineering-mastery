from uuid import UUID
from sqlalchemy.orm import Session
from app.models.cart import Carts
from app.models.cart_item import CartItems

class CartRepository:

    def get_cart_by_user_id(self, db: Session, user_id: UUID):
        return db.query(Carts).filter(Carts.user_id == user_id).first()

    def create_cart(self, db: Session, user_id: UUID):
        new_cart = Carts(user_id=user_id)
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart

    def get_cart_items(self, db: Session, cart_id: int):
        return db.query(CartItems).filter(CartItems.cart_id == cart_id).all()

    def get_cart_item_by_id(self, db: Session, item_id: int):
        return db.query(CartItems).filter(CartItems.cart_item_id == item_id).first()

    def get_item_in_cart_by_product(self, db: Session, cart_id: int, product_id: int):
        return db.query(CartItems).filter(
            CartItems.cart_id == cart_id,
            CartItems.product_id == product_id
        ).first()

    def add_item_to_cart(self, db: Session, cart_item: CartItems):
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    def update_item_quantity(self, db: Session, item_id: int, quantity: int):
        item = self.get_cart_item_by_id(db, item_id)
        if item:
            item.quantity = quantity
            db.commit()
            db.refresh(item)
        return item

    def delete_cart_item(self, db: Session, item_id: int):
        item = self.get_cart_item_by_id(db, item_id)
        if item:
            db.delete(item)
            db.commit()
        return item