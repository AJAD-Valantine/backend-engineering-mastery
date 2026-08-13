from uuid import UUID
from app.exceptions.cart_item import CartItemNotFound, NotEnoughStockAvailable
from app.models.cart_item import CartItems
from app.repository.cart_item import CartRepository
from app.schemas.cart_item import CartItemCreateRequest, CartItemUpdateRequest
from app.services.product import ProductService
from app.services.user import UserService

class CartService:

    def __init__(self) -> None:
        self.cart_repo = CartRepository()
        self.user_service = UserService()
        self.product_service = ProductService()

    def _get_or_create_cart(self, db, user_id: UUID):
        """Helper to fetch the user's cart, or create it if it doesn't exist."""
        cart = self.cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            cart = self.cart_repo.create_cart(db, user_id)
        return cart

    def add_to_cart(self, db, user_id: UUID, request: CartItemCreateRequest):
        product = self.product_service.get_product_by_id(db, request.product_id)

        if product.stock_quantity < request.quantity:
            raise NotEnoughStockAvailable("Not enough stock available")

        cart = self._get_or_create_cart(db, user_id)

        existing_item = self.cart_repo.get_item_in_cart_by_product(db, cart.cart_id, request.product_id)

        if existing_item:
            new_quantity = existing_item.quantity + request.quantity
            if product.stock_quantity < new_quantity:
                raise NotEnoughStockAvailable("Not enough stock to add more of this item")

            return self.cart_repo.update_item_quantity(db, existing_item.cart_item_id, new_quantity)

        new_item = CartItems(
            cart_id=cart.cart_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
        return self.cart_repo.add_item_to_cart(db, new_item)

    def view_cart(self, db, user_id: UUID):
        cart = self.cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            return []
        return self.cart_repo.get_cart_items(db, cart.cart_id)

    def view_cart_item_by_id(self, db, user_id: UUID, item_id: int):
        cart = self.cart_repo.get_cart_by_user_id(db, user_id)
        if not cart:
            raise CartItemNotFound("Cart not found")

        item = self.cart_repo.get_cart_item_by_id(db, item_id)
        if not item or item.cart_id != cart.cart_id:
            raise CartItemNotFound("Cart item not found")

        return item

    def update_quantity(self, db, user_id: UUID, item_id: int, request: CartItemUpdateRequest):
        item = self.view_cart_item_by_id(db, user_id, item_id)
        product = self.product_service.get_product_by_id(db, item.product_id)

        if product.stock_quantity < request.quantity:
            raise NotEnoughStockAvailable("Not enough stock available for this quantity")

        return self.cart_repo.update_item_quantity(db, item_id, request.quantity)

    def remove_cart_item(self, db, user_id: UUID, item_id: int):
        item = self.view_cart_item_by_id(db, user_id, item_id)
        return self.cart_repo.delete_cart_item(db, item.cart_item_id)