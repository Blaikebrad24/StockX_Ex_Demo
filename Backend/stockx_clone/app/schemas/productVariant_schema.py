from pydantic import BaseModel
from typing import Optional

class ProductVariantBase(BaseModel):
    size: Optional[str]
    color: Optional[str]
    sku: Optional[str]

class ProductVariantCreate(ProductVariantBase):
    product_id: int

class ProductVariantOut(ProductVariantBase):
    id: int
    product_id: int

    class Config:
        orm_mode = True