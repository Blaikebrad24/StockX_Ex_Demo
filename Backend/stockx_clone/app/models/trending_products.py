from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.database import Base

class TrendingProduct(Base):
    __tablename__ = "trending_products"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    score = Column(DECIMAL(10, 2), nullable=False)
    trend_direction = Column(String(10))
    updated_at = Column(DateTime(timezone=True), server_default=func.now())