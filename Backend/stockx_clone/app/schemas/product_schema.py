from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: Optional[str]
    model: Optional[str]
    gender: Optional[str]
    condition: Optional[str]
    category: Optional[str]
    listing_type: Optional[str]
    thumbnail_url: Optional[str]
    description: Optional[str]
    retail_price: Optional[float]
    last_sale_price: Optional[float]
    last_sale_date: Optional[datetime]
    average_price: Optional[float]
    sales_count: Optional[int]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
