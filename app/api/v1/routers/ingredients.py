
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ingredient import IngredientResponse, IngredientCreate, IngredientUpdate
from app.services.ingredient_service import IngredientService
from app.db.database import get_db

from typing import Optional

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

# Mock data
# TODO: Delete mock data
MOCK_INGREDIENTS = [
    {"id": 1, "name": "Flour", "stock_quantity": 50.0, "unit": "kg", "current_unit_price": 40.5},
    {"id": 2, "name": "Sugar", "stock_quantity": 20.0, "unit": "kg", "current_unit_price": 20.0},
    {"id": 3, "name": "Vanilla Extract", "stock_quantity": 2.5, "unit": "liters", "current_unit_price": 50.0},
]


@router.get("/", response_model=list[IngredientResponse])
async def get_ingredients(db: AsyncSession = Depends(get_db)):
    """
    Retrieve a list of all ingredients in the bakery's inventory.
    """
    return await IngredientService.get_all(db)


@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient_by_id(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a specific ingredient by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'products_list'.
    """
    db_ingredient = await IngredientService.get_by_id(db, ingredient_id)

    if not db_ingredient:    
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )
    
    return db_ingredient


@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(ingredient_in: IngredientCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new ingredient in the inventory.
    
    UI Note: On successful creation, the frontend should show a success toast 
    and redirect the user to 'products_list'.
    """
    db_ingredient = await IngredientService.get_by_name(db, ingredient_in.name)
    if db_ingredient is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name '{ingredient_in.name}' already exists."
        )
    
    return await IngredientService.create(db, ingredient_in)


@router.patch("/{ingredient_id}", response_model=IngredientResponse, status_code=status.HTTP_200_OK)
async def update_ingredient(
    ingredient_id: int, 
    ingredient: IngredientUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update an existing ingredient in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'products_list' route.
    """
    db_ingredient = await IngredientService.get_by_id(db, ingredient_id)
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id '{ingredient_id}' not found"
        )
    
    if ingredient.name is not None and ingredient.name != db_ingredient.name:
        existing_name = await IngredientService.get_by_name(db, ingredient.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with name '{ingredient.name}' already exists."
            )

    update_data = ingredient.model_dump(exclude_unset=True)  # get explicit values and ignore nulls
    updated_ingredient = await IngredientService.update(db, db_ingredient, update_data)

    return updated_ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an ingredient from the inventory.
    
    UI Note: On successful deletion (204), remove the item from the local 
    state or refetch the list, and ensure the user is on 'products_list'.
    """
    db_ingredient = await IngredientService.get_by_id(db, ingredient_id)
    if not db_ingredient:   
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id '{ingredient_id}' not found"
        )

    return await IngredientService.delete(db, db_ingredient)
