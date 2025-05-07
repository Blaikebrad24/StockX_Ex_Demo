from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None
    condition: Optional[str] = None
    category: Optional[str] = None
    listing_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    retail_price: Optional[Decimal] = None

class ProductCreate(ProductBase):
    last_sale_price: Optional[Decimal] = None
    last_sale_date: Optional[datetime] = None
    average_price: Optional[Decimal] = None
    sales_count: Optional[int] = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None
    condition: Optional[str] = None
    category: Optional[str] = None
    listing_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    retail_price: Optional[Decimal] = None
    last_sale_price: Optional[Decimal] = None
    last_sale_date: Optional[datetime] = None
    average_price: Optional[Decimal] = None
    sales_count: Optional[int] = None

class ProductResponse(ProductBase):
    id: int
    last_sale_price: Optional[Decimal] = None
    last_sale_date: Optional[datetime] = None
    average_price: Optional[Decimal] = None
    sales_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Using from_attributes instead of orm_mode