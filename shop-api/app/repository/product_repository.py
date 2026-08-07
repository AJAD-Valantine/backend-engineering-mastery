from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product_model import Products
from app.schemas.product_schema import ProductUpdateRequest


class ProductRepository:
    def create_product(self, db: Session, product: Products):

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def read_all_products(self, db: Session, skip: int = 0, limit: int = 10):

        total_items = db.query(func.count(Products.product_id)).scalar()
        
        products = db.query(Products).offset(skip).limit(limit).all()
        
        return total_items, products

    def read_product_by_id(self, db: Session, product_id: int):

        return db.query(Products).filter(Products.product_id == product_id).first()

    def update_product(
        self, db: Session, product_id: int, request: ProductUpdateRequest
    ):

        product = db.query(Products).filter(Products.product_id == product_id).first()

        update_data = request.model_dump(exclude_unset=True)

        if product is not None:
            for key, value in update_data.items():
                setattr(product, key, value)

            db.commit()
            db.refresh(product)

            return product

    def delete_product(self, db: Session, product_id: int):

        product = db.query(Products).filter(Products.product_id == product_id).first()

        db.delete(product)
        db.commit()

        return product
