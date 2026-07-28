from app.exceptions.base_exception import ShopException
from app.exceptions.product_exceptions import ProductNotFound
from app.presentation.schemas.product_schema import ProductResponse
from app.presentation.schemas.response_model import error_response, success_response
from app.services.product_service import ProductService


class ProductController:
    def __init__(self) -> None:
        self.product_service = ProductService()

    def create_product(self, db, request):

        try:
            raw_product = self.product_service.add_product(db, request)

            product = ProductResponse.model_validate(raw_product).model_dump()
            return success_response(product, "product created successfully")

        except ShopException as e:
            return error_response(str(e), 500)

    def get_all_products(self, db):

        try:
            raw_products = self.product_service.get_all_products(db)
            products = [
                ProductResponse.model_validate(product).model_dump()
                for product in raw_products
            ]

            if products:
                return success_response(products, "fetched all products")
            else:
                return error_response("no products available", 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def get_product_by_id(self, db, product_id):

        try:
            raw_product = self.product_service.get_product_by_id(db, product_id)
            product = ProductResponse.model_validate(raw_product).model_dump()
            return success_response(product, "fetched product")

        except ProductNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def update_product(self, db, product_id, request):

        try:
            raw_product = self.product_service.update_product(db, product_id, request)
            product = ProductResponse.model_validate(raw_product).model_dump()
            return success_response(product, "product updated")

        except ProductNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)

    def remove_product(self, db, product_id):

        try:
            raw_product = self.product_service.remove_product(db, product_id)
            product = ProductResponse.model_validate(raw_product).model_dump()
            return success_response(product, "product deleted")

        except ProductNotFound as e:
            return error_response(str(e), 404)

        except ShopException as e:
            return error_response(str(e), 500)
