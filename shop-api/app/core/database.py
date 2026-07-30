from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Create Session
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=True,
                            bind=engine)

# Base Class
class Base(DeclarativeBase):
    pass

# Creating DB Tables
from app.models import cart_item_model, product_model, order_item_model, order_model, payment_model, user_model #noqa

def init_models():

    Base.metadata.create_all(bind=engine)