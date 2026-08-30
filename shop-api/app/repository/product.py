from sqlalchemy.orm import Session

from app.models.product import Products


class ProductRepository:

    def __init__(
            self,
            db : Session
    ) -> None:

        self.db: Session = db

    def create_product(
            self,
            product: Products
    ) -> Products:

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        return product

    def read_all_products(self) -> list[Products]:

        products: list[Products] = self.db.query(Products).all()

        return products

    def read_product_by_id(
            self,
            product_id: int
    ) -> Products | None:

        return self.db.query(Products).filter(Products.product_id == product_id).first()

    def update_product(
            self,
            product_id: int,
            update_data: dict
    ) -> Products | None:

        product: Products | None = self.db.query(Products).filter(Products.product_id == product_id).first()

        if product is not None:
            for key, value in update_data.items():
                setattr(product, key, value)

            self.db.commit()
            self.db.refresh(product)

        return product

    def delete_product(
            self,
            product_id: int
    ) -> Products | None:

        product: Products | None = self.db.query(Products).filter(Products.product_id == product_id).first()

        self.db.delete(product)
        self.db.commit()
