from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    stock_quantity: float
    unit: str  # kg, lts, pz


class IngredientResponse(IngredientBase):
    id: int    

    class Config:
        from_attributes = True
