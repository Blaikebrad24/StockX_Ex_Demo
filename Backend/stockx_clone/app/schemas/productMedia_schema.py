from pydantic import BaseModel
from typing import Optional

class ProductMediaBase(BaseModel):
    product_id: int
    media_url: str
    media_type: str
    is_primary: Optional[bool] = False
    position: Optional[int] = 0
    caption: Optional[str]

class ProductMediaOut(ProductMediaBase):
    id: int

    class Config:
        orm_mode = True