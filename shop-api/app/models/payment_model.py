from datetime import datetime
from decimal import Decimal

from app.core.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True, 
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending")
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())