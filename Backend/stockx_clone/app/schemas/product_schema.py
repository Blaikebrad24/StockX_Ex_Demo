from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class ProductBase(BaseModel):
    name: str
    slug: str
    style_id: Optional[str]
    description: Optional[str]
    release_date: Optional[date]
    colorway: Optional[str]
    retail_price: Optional[float]
    gender: Optional[str]
    thumbnail_url: Optional[str]

class ProductCreate(ProductBase):
    brand_id: int
    primary_category_id: Optional[int]

class ProductOut(ProductBase):
    id: int
    brand_id: int
    primary_category_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    last_sale_price: Optional[float]
    last_sale_date: Optional[datetime]
    sales_count: int

    class Config:
        orm_mode = True
