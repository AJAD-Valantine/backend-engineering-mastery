import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())