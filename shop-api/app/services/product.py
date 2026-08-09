from app.exceptions.product import ProductNotFound
from app.models.product import Products
from app.repository.product import ProductRepository
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
)


class ProductService:

    def __init__(self) -> None:
        self.product_repository = ProductRepository()

    def add_product(
            self,
            db,
            product: ProductCreateRequest
    ):

        data = Products(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category=product.category,
        )

        return self.product_repository.create_product(
                                            db=db,
                                            product=data)

    def get_all_products(
            self,
            db,
            page: int = 1,
            size: int = 10
    ):
        
        skip = (page - 1) * size
        total_items, products = self.product_repository.read_all_products(db, skip=skip, limit=size)
        
        return {
            "total_items": total_items,
            "page": page,
            "size": size,
            "data": products
        }

    def get_product_by_id(
            self,
            db,
            product_id: int
    ):

        product = self.product_repository.read_product_by_id(db, product_id)

        if product is None:
            raise ProductNotFound("product not found")

        return product

    def update_product(
            self,
            db,
            product_id,
            request: ProductUpdateRequest
    ):

        product_result = self.product_repository.read_product_by_id(db, product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        update_data = request.model_dump(exclude_unset=True)

        return self.product_repository.update_product(
            db=db,
            product_id=product_id,
            update_data=update_data
        )

    def remove_product(
            self,
            db,
            product_id):

        product_result = self.product_repository.read_product_by_id(db, product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        return self.product_repository.delete_product(db, product_id)
