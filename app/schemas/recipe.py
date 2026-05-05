from pydantic import BaseModel
from typing import List, Optional


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientUpdate(RecipeIngredientBase):
    pass


class RecipeIngredientResponse(RecipeIngredientBase):
    ingredient_name: str
    ingredient_unit: str


class RecipeBase(BaseModel):
    name: str
    description: str
    is_active: bool = True


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate]


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    ingredients: Optional[List[RecipeIngredientUpdate]] = None


class RecipeResponse(RecipeBase):
    id: int
    ingredients: List[RecipeIngredientResponse]

    class Config:
        from_attributes = True