from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    gender = Column(String(20))
    condition = Column(String(50))
    category = Column(String(100))
    listing_type = Column(String(50))
    thumbnail_url = Column(Text)
    description = Column(Text)
    retail_price = Column(DECIMAL(10, 2))
    last_sale_price = Column(DECIMAL(10, 2))
    last_sale_date = Column(DateTime(timezone=True))
    average_price = Column(DECIMAL(10, 2))
    sales_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())