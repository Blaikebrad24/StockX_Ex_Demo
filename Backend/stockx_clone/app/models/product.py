from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, DECIMAL, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"))
    primary_category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    style_id = Column(String(50))
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    release_date = Column(Date)
    colorway = Column(String(100))
    retail_price = Column(DECIMAL(10, 2))
    gender = Column(String(20))
    thumbnail_url = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_sale_price = Column(DECIMAL(10, 2))
    last_sale_date = Column(DateTime(timezone=True))
    sales_count = Column(Integer, default=0)