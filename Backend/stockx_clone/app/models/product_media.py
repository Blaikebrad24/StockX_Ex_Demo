from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.database import Base

class ProductMedia(Base):
    __tablename__ = "product_media"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    media_url = Column(String, nullable=False)
    media_type = Column(String(20), nullable=False)
    is_primary = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    caption = Column(String(255))