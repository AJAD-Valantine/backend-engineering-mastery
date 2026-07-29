from app.config import SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Create Session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=True,
                            bind=engine)

# Base Class
class Base(DeclarativeBase):
    pass

#Dependency
def db_connection():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Creating DB Tables
from app.models import cart_item_model, customer_model, product_model, order_item_model, order_model, payment_model #noqa

def init_models():

    Base.metadata.create_all(bind=engine)