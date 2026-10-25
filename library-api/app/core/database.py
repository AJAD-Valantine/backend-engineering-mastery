from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.session import Session

from app.core.config import Settings, get_settings

settings: Settings = get_settings()

engine: Engine = create_engine(
    url=settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # UniqueConstraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # CheckConstraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # ForeignKey
    "pk": "pk_%(table_name)s",  # PrimaryKey
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

class Base(DeclarativeBase):
    metadata = metadata
