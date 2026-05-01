from pydantic import BaseModel
from typing import Optional


class IngredientBase(BaseModel):
    name: str
    stock_quantity: float
    unit: str  # kg, lts, pz


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit: Optional[str] = None


class IngredientResponse(IngredientBase):
    id: int    

    class Config:
        from_attributes = True
