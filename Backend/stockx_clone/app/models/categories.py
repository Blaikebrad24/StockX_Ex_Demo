from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UniqueConstraint
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("name", "parent_id"),)