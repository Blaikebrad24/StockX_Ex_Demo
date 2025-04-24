from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    size = Column(String(20))
    color = Column(String(50))
    sku = Column(String(100))

    __table_args__ = (UniqueConstraint("product_id", "size", "color"),)