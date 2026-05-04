from pydantic import BaseModel
from typing import List


class RecipeBase(BaseModel):
    name: str
    description: str
    is_active: bool = True


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float


class RecipeIngredientResponse(RecipeIngredientCreate):
    ingredient_name: str
    ingredient_unit: str
    

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate]


class RecipeResponse(RecipeBase):
    id: int
    ingredients: List[RecipeIngredientResponse]

    class Config:
        from_attributes = True
