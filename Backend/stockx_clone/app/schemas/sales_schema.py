from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SaleBase(BaseModel):
    variant_id: Optional[int]
    ask_id: Optional[int]
    bid_id: Optional[int]
    seller_id: Optional[UUID]
    buyer_id: Optional[UUID]
    sale_price: float
    stripe_payment_intent_id: Optional[str]
    status: Optional[str] = "completed"

class SaleCreate(SaleBase):
    pass

class SaleOut(SaleBase):
    id: int
    sale_date: datetime

    class Config:
        orm_mode = True
