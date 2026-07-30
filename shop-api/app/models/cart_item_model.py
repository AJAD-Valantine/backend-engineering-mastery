from datetime import datetime

from app.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, UUID, func
from sqlalchemy.orm import Mapped, mapped_column


class CartItems(Base):
    __tablename__ = "cart_items"

    cart_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())