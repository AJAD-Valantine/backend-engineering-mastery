from uuid import UUID

from sqlalchemy.orm import Session

from app.models.cart import Carts
from app.models.cart_item import CartItems


class CartRepository:

    def __init__(
            self,
            db : Session
    ) -> None:

        self.db = db

    def get_cart_by_user_id(
            self,
            user_id: UUID
    ) -> Carts | None:

        return self.db.query(Carts).filter(Carts.user_id == user_id).first()

    def create_cart(
            self,
            user_id: UUID
    ) -> Carts:

        new_cart = Carts(user_id=user_id)

        self.db.add(new_cart)
        self.db.commit()
        self.db.refresh(new_cart)

        return new_cart

    def get_cart_items(
            self,
            cart_id: int
    ) -> list[CartItems]:

        return self.db.query(CartItems).filter(CartItems.cart_id == cart_id).all()

    def get_cart_item_by_id(
            self,
            item_id: int
    ) -> CartItems | None:

        return self.db.query(CartItems).filter(CartItems.cart_item_id == item_id).first()

    def get_item_in_cart_by_product(
            self,
            cart_id: int,
            product_id: int
    ) -> CartItems | None:

        return self.db.query(CartItems).filter(
            CartItems.cart_id == cart_id,
            CartItems.product_id == product_id
        ).first()

    def add_item_to_cart(
            self,
            cart_item: CartItems
    ) -> CartItems:

        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)

        return cart_item

    def update_item_quantity(
            self,
            item_id: int,
            quantity: int
    ) -> CartItems:

        cart_item = self.get_cart_item_by_id(item_id)

        if cart_item:
            cart_item.quantity = quantity
            self.db.commit()
            self.db.refresh(cart_item)

        return cart_item

    def delete_cart_item(
            self,
            item_id: int
    ) -> CartItems:

        cart_item = self.get_cart_item_by_id(item_id)

        if cart_item:
            self.db.delete(cart_item)
            self.db.commit()