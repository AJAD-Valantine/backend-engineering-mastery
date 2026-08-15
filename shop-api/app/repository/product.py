from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Products


class ProductRepository:

    def __init__(
            self,
            db : Session
    ) -> None:

        self.db = db

    def create_product(
            self,
            product: Products
    ) -> Products:

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def read_all_products(
            self,
            skip: int = 0,
            limit: int = 10
    ) -> tuple[int, list[Products]]:

        total_items = self.db.query(func.count(Products.product_id)).scalar()
        products = self.db.query(Products).offset(skip).limit(limit).all()
        
        return total_items, products

    def read_product_by_id(
            self,
            product_id: int
    ) -> Products | None:

        return self.db.query(Products).filter(Products.product_id == product_id).first()

    def update_product(
            self,
            product_id: int,
            update_data: dict
    ) -> Products:

        product = self.db.query(Products).filter(Products.product_id == product_id).first()

        if product is not None:
            for key, value in update_data.items():
                setattr(product, key, value)

            self.db.commit()
            self.db.refresh(product)

        return product

    def delete_product(
            self,
            product_id: int
    ) -> Products:

        product = self.db.query(Products).filter(Products.product_id == product_id).first()

        self.db.delete(product)
        self.db.commit()