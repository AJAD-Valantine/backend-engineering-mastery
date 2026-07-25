from uuid import UUID
from sqlalchemy.orm import Session
from app.models.order_model import Orders
from app.models.order_item_model import OrderItems

class OrderRepository:

    def create_order(self, db: Session, order: Orders):
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def create_order_items(self, db: Session, order_items: list[OrderItems]):
        db.add_all(order_items)
        db.commit()
        return order_items

    def read_all_orders(self, db: Session):
        return db.query(Orders).all()
    
    def read_order_by_id(self, db: Session, order_id: int):
        return db.query(Orders).filter(Orders.id == order_id).first()

    def read_order_by_customer_id(self, db: Session, customer_id: UUID):
        return db.query(Orders).filter(Orders.customer_id == customer_id).all()
    
    def update_status(self, db: Session, order_id: int, status: str):
        order = self.read_order_by_id(db, order_id)
        
        if order is None:
            return None

        order.status = status
        db.commit()
        db.refresh(order)
        return order