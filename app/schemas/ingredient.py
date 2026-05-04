from pydantic import BaseModel
from typing import Optional


class IngredientBase(BaseModel):
    name: str
    stock_quantity: float
    unit: str  # kg, lts, pz
    current_unit_price: float
    is_active: bool = True  # set True for new ingredients


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit: Optional[str] = None
    current_unit_price: Optional[float] = None
    is_active: Optional[bool] = None


class IngredientResponse(IngredientBase):
    id: int    

    class Config:
        from_attributes = True
