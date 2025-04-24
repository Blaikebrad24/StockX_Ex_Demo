from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"))
    ask_id = Column(Integer, ForeignKey("asks.id", ondelete="SET NULL"))
    bid_id = Column(Integer, ForeignKey("bids.id", ondelete="SET NULL"))
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    sale_price = Column(DECIMAL(10, 2), nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    stripe_payment_intent_id = Column(String(255))
    status = Column(String(20), default="completed")