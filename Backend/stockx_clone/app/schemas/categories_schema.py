from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None

class CategoryOut(CategoryBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True