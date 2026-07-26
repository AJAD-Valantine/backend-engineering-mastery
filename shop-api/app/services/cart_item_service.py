from uuid import UUID

from app.exceptions.cart_item_exceptions import (
    CartItemNotFound,
    NotEnoughStockAvailable,
)
from app.models.cart_item_model import CartItems
from app.presentation.schemas.cart_item_schema import (
    CartItemCreateRequest,
    CartItemUpdateRequest,
)
from app.repository.cart_item_repository import CartItemRepository
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService


class CartItemService:
    def __init__(self) -> None:
        self.cart_item_repository = CartItemRepository()
        self.customer_service = CustomerService()
        self.product_service = ProductService()

    def add_to_cart(self, db, cart_item: CartItemCreateRequest):

        self.customer_service.get_customer_by_id(db, cart_item.customer_id)
        product = self.product_service.get_product_by_id(db, cart_item.product_id)

        if product.stock_quantity < cart_item.quantity:
            raise NotEnoughStockAvailable("Not enough stock available")

        existing_cart = self.cart_item_repository.read_cart(db, cart_item.customer_id)

        existing_item = None
        for item in existing_cart:
            if item.product_id == cart_item.product_id:
                existing_item = item
                break

        if existing_item:
            new_total_quantity = existing_item.quantity + cart_item.quantity

            if product.stock_quantity < new_total_quantity:
                raise NotEnoughStockAvailable(
                    "Not enough stock to add more of this item"
                )

            return self.cart_item_repository.update_quantity(
                db, existing_item.cart_id, new_total_quantity
            )

        else:
            new_cart_model = CartItems(
                customer_id=cart_item.customer_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )

            return self.cart_item_repository.create_cart_item(db, new_cart_model)

    def view_cart(self, db, customer_id: UUID):

        return self.cart_item_repository.read_cart(db, customer_id)

    def view_cart_item_by_id(self, db, cart_item_id):

        cart_item = self.cart_item_repository.read_cart_item_by_id(db, cart_item_id)

        if cart_item is None:
            raise CartItemNotFound("cart item not found")

        return cart_item

    def update_quantity(
        self, db, cart_item_id, update_cart_item: CartItemUpdateRequest
    ):

        cart_item = self.view_cart_item_by_id(db, cart_item_id)

        product = self.product_service.get_product_by_id(db, cart_item.product_id)

        if product.stock_quantity < update_cart_item.quantity:
            raise NotEnoughStockAvailable(
                "Not enough stock available for this quantity"
            )

        updated_item = self.cart_item_repository.update_quantity(
            db, cart_item_id, update_cart_item.quantity
        )

        return updated_item

    def remove_cart_item(self, db, cart_item_id):

        cart_item = self.cart_item_repository.delete_cart_item(db, cart_item_id)

        if cart_item is None:
            raise CartItemNotFound("cart item not found")

        return cart_item
