from app.exceptions.product_exceptions import ProductNotFound
from app.models.product_model import Products
from app.presentation.schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.repository.product_repository import ProductRepository


class ProductService:
    def __init__(self) -> None:
        self.product_repository = ProductRepository()

    def add_product(self, db, product: ProductCreateRequest):

        data = Products(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category=product.category,
        )

        return self.product_repository.create_product(db, data)

    def get_all_products(self, db):

        return self.product_repository.read_all_products(db)

    def get_product_by_id(self, db, product_id: int):

        product = self.product_repository.read_product_by_id(db, product_id)

        if product is None:
            raise ProductNotFound("product not found")

        return product

    def update_product(self, db, product_id, product: ProductUpdateRequest):

        product_result = self.product_repository.read_product_by_id(db, product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        return self.product_repository.update_product(db, product_id, product)

    def remove_product(self, db, product_id):

        product_result = self.product_repository.read_product_by_id(db, product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        return self.product_repository.delete_product(db, product_id)
