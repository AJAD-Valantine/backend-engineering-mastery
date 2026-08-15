from app.exceptions.product import ProductNotFound
from app.models.product import Products
from app.repository.product import ProductRepository
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from PIL import UnidentifiedImageError
from app.core.image_utils import process_image, delete_image
from app.exceptions.image import InvalidImageFile
from pathlib import Path
from app.core.config import settings

PRODUCT_PICS_DIR = Path(settings.media_root) / "product_pics"

class ProductService:

    def __init__(self, product_repository : ProductRepository) -> None:
        self.product_repository = product_repository

    def add_product(
            self,
            product: ProductCreateRequest
    ):

        data = Products(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
            category=product.category,
        )

        return self.product_repository.create_product(data)

    def get_all_products(
            self,
            page: int = 1,
            size: int = 10
    ):
        
        skip = (page - 1) * size
        total_items, products = self.product_repository.read_all_products(
            skip=skip,
            limit=size
        )
        
        return {
            "total_items": total_items,
            "page": page,
            "size": size,
            "data": products
        }

    def get_product_by_id(
            self,
            product_id: int
    ):

        product = self.product_repository.read_product_by_id(product_id)

        if product is None:
            raise ProductNotFound("product not found")

        return product

    def update_product(
            self,
            product_id,
            request: ProductUpdateRequest
    ):

        product_result = self.product_repository.read_product_by_id(product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        update_data = request.model_dump(exclude_unset=True)

        return self.product_repository.update_product(
            product_id=product_id,
            update_data=update_data
        )

    def remove_product(
            self,
            product_id):

        product_result = self.product_repository.read_product_by_id(product_id)

        if product_result is None:
            raise ProductNotFound("product not found")

        return self.product_repository.delete_product(product_id)


    def upload_product_image(
            self,
            product_id: int,
            file_bytes: bytes
    ):
        product = self.product_repository.read_product_by_id(product_id)
        if product is None:
            raise ProductNotFound("product not found")

        old_filename = product.image_file

        try:
            new_filename = process_image(
                file_bytes=file_bytes,
                destination_folder=PRODUCT_PICS_DIR,
                dimension=settings.product_pic_size
            )
        except UnidentifiedImageError:
            raise InvalidImageFile()

        updated_product = self.product_repository.update_product(
            product_id=product_id,
            update_data={"image_file": new_filename}
        )

        if old_filename:
            delete_image(old_filename, PRODUCT_PICS_DIR)

        return updated_product


    def remove_product_image(
            self,
            product_id: int
    ):
        product = self.product_repository.read_product_by_id(product_id)
        if product is None:
            raise ProductNotFound("product not found")

        if product.image_file is None:
            return product

        old_filename = product.image_file

        updated_product = self.product_repository.update_product(
            product_id=product_id,
            update_data={"image_file": None}
        )

        delete_image(old_filename, PRODUCT_PICS_DIR)

        return updated_product