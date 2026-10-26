from core.config import Settings, get_settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm.session import Session

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
class Base(DeclarativeBase):
    pass
