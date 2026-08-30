from typing import Any

from app.exceptions.product import ProductNotFound
from app.models.product import Products
from app.repository.product import ProductRepository
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
)


class ProductService:

    def __init__(self, product_repository : ProductRepository) -> None:
        self.product_repository: ProductRepository = product_repository

    def add_product(
            self,
            product: ProductCreateRequest
    ) -> Products:

        data = Products(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category=product.category,
        )

        return self.product_repository.create_product(data)

    def get_all_products(self) -> list[Products]:

        return self.product_repository.read_all_products()

    def get_product_by_id(
            self,
            product_id: int
    ) -> Products:

        product: Products | None = self.product_repository.read_product_by_id(product_id)

        if product is None:
            raise ProductNotFound("product not found")

        return product

    def update_product(
            self,
            product_id,
            request: ProductUpdateRequest
    ) -> Products:

        product_result: Products | None = self.product_repository.read_product_by_id(product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        update_data: dict[str, Any] = request.model_dump(exclude_unset=True)

        return self.product_repository.update_product(
            product_id=product_id,
            update_data=update_data
        )

    def remove_product(
            self,
            product_id) -> Products:

        product_result: Products | None = self.product_repository.read_product_by_id(product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        return self.product_repository.delete_product(product_id)
