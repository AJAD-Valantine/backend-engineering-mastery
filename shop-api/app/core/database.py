from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

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
from app.models import cart_item, product, order_item, order, payment, user #noqa

def init_models():

    Base.metadata.create_all(bind=engine)