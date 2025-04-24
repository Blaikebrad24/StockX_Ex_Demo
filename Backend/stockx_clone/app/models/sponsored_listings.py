from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SponsoredListing(Base):
    __tablename__ = "sponsored_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    sponsor_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())