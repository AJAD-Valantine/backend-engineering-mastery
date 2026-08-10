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