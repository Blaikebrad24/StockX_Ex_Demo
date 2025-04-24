from sqlalchemy import Column, Integer, Boolean, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), primary_key=True)
    desired_price = Column(DECIMAL(10, 2))
    notify_on_price = Column(Boolean, default=False)
    notify_on_restock = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())