from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MeasurementUnit(str, Enum):
    KG = "kg"
    G = "g"      # Gramos
    L = "l"      # Litros
    ML = "ml"    
    PZA = "pza"  
    CAJA = "caja"


class IngredientCategory(str, Enum):
    LACTEOS = "lacteos"
    SECOS = "secos"
    LIQUIDOS = "liquidos"
    FRUTAS_VERDURAS = "frutas_verduras"
    ESPECIAS = "especias"


class IngredientBase(BaseModel):
    name: str
    stock_quantity: float
    unit: MeasurementUnit
    category: IngredientCategory
    current_unit_price: float
    is_active: bool = True  # set True for new ingredients


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit: Optional[MeasurementUnit] = None
    category: Optional[IngredientCategory] = None
    current_unit_price: Optional[float] = None
    is_active: Optional[bool] = None


class IngredientResponse(IngredientBase):
    id: int    

    class Config:
        from_attributes = True
