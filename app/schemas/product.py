from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ProductCategory(str, Enum):
    CAKES = "Cakes"
    SLICES = "Slices"
    INDIVIDUAL_DESSERTS = "Individual Desserts"
    BEVERAGES = "Beverages" 


class ProductBase(BaseModel):
    name: str
    description: str
    sale_price: float  # admin will select the sale price
    category: str
    recipe_id: int
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sale_price: Optional[float] = None
    category: Optional[str] = None
    recipe_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    cost: Optional[float] = None  # calculated field

    class Config:
        from_attributes = True
