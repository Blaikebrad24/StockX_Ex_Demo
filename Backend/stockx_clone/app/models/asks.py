from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Ask(Base):
    __tablename__ = "asks"

    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"))
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    price = Column(DECIMAL(10, 2), nullable=False)
    condition = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    expires_at = Column(DateTime(timezone=True))
    is_instant = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())