from app.exceptions.base_exception import ShopException
from app.exceptions.product_exceptions import ProductNotFound
from app.services.product_service import ProductService
from fastapi import HTTPException, status


class ProductController:
    
    def __init__(self) -> None:
        self.product_service = ProductService()

    def create_product(self, db, request):
        try:
            return self.product_service.add_product(db, request)

        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_all_products(self, db):
        try:
            products = self.product_service.get_all_products(db)
            
            if not products:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no products available")
            
            return products

        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_product_by_id(self, db, product_id):
        try:
            return self.product_service.get_product_by_id(db, product_id)

        except ProductNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update_product(self, db, product_id, request):
        try:
            return self.product_service.update_product(db, product_id, request)

        except ProductNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def remove_product(self, db, product_id):
        try:
            return self.product_service.remove_product(db, product_id)

        except ProductNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))