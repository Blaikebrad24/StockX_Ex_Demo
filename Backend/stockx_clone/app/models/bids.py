from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"))
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="active")
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())