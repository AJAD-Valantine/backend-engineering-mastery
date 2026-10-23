from core.config import Settings
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

settings = Settings()  # type: ignore[call-arg]

engine: Engine = create_engine(
    url=settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class Base(DeclarativeBase):
    pass
