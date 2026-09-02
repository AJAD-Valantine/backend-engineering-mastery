from uuid import UUID

from fastapi import HTTPException, status

from app.models.cart_item import CartItems
from app.repository.cart_item import CartRepository
from app.schemas.cart_item import CartItemCreateRequest, CartItemUpdateRequest
from app.services.product import ProductService
from app.services.user import UserService

from ..models.cart import Carts
from ..models.product import Products


class CartService:

    def __init__(
            self,
            cart_repository : CartRepository,
            user_service : UserService,
            product_service : ProductService
    ) -> None:
        self.cart_repository = cart_repository
        self.user_service = user_service
        self.product_service = product_service

    def _get_or_create_cart(
            self,
            user_id: UUID
    ):
        """Helper to fetch the user's cart, or create it if it doesn't exist."""
        cart = self.cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            cart = self.cart_repository.create_cart(user_id)
        return cart

    def add_to_cart(
            self,
            user_id: UUID,
            request: CartItemCreateRequest
    ):
        product = self.product_service.get_product_by_id(request.product_id)

        if product.stock_quantity < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock available"
                )

        cart: Carts = self._get_or_create_cart(user_id)

        existing_item: CartItems | None = self.cart_repository.get_item_in_cart_by_product(
            cart.cart_id,
            request.product_id
        )

        if existing_item:
            new_quantity: int = existing_item.quantity + request.quantity

            if product.stock_quantity < new_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not enough stock to add more of this item",
                )

            return self.cart_repository.update_item_quantity(
                existing_item.cart_item_id,
                new_quantity
            )

        new_item = CartItems(
            cart_id=cart.cart_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
        
        return self.cart_repository.add_item_to_cart(new_item)

    def view_cart(
            self,
            user_id: UUID
    ):
        cart: Carts | None = self.cart_repository.get_cart_by_user_id(user_id)
        if not cart:
            return []
        return self.cart_repository.get_cart_items(cart.cart_id)

    def view_cart_item_by_id(
            self,
            user_id: UUID,
            item_id: int
    ) -> CartItems:
        cart: Carts | None = self.cart_repository.get_cart_by_user_id(user_id)

        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        item: CartItems | None = self.cart_repository.get_cart_item_by_id(item_id)

        if not item or item.cart_id != cart.cart_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
                )

        return item

    def update_quantity(
            self,
            user_id: UUID,
            item_id: int,
            request: CartItemUpdateRequest
    ) -> CartItems:
        item: CartItems = self.view_cart_item_by_id(
            user_id,
            item_id
        )
        product: Products = self.product_service.get_product_by_id(item.product_id)

        if product.stock_quantity < request.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough stock available for this quantity",
            )

        return self.cart_repository.update_item_quantity(
            item_id,
            request.quantity
        )

    def remove_cart_item(
            self,
            user_id: UUID,
            item_id: int
    ) -> CartItems:
        item: CartItems = self.view_cart_item_by_id(
            user_id,
            item_id
        )
        return self.cart_repository.delete_cart_item(item.cart_item_id)
