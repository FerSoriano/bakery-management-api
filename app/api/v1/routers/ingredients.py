
from fastapi import APIRouter, HTTPException, status, Response
from app.schemas.ingredient import IngredientResponse, IngredientCreate, IngredientUpdate, IngredientBase

from typing import Optional

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

# Mock data
MOCK_INGREDIENTS = [
    {"id": 1, "name": "Flour", "stock_quantity": 50.0, "unit": "kg"},
    {"id": 2, "name": "Sugar", "stock_quantity": 20.0, "unit": "kg"},
    {"id": 3, "name": "Vanilla Extract", "stock_quantity": 2.5, "unit": "liters"},
]


def is_name_duplicated(name: str, exclude_id: Optional[int] = None) -> bool:
    """
    Check if an ingredient name already exists in the mock database.
    Case-insensitive. Optionally excludes a specific ID (useful for updates).
    """
    for i in MOCK_INGREDIENTS:
        if i["name"].lower() == name.lower() and i["id"] != exclude_id:
            return True
    return False


@router.get("/", response_model=list[IngredientResponse])
async def get_ingredients():
    """
    Retrieve a list of all ingredients in the bakery's inventory.
    """
    return MOCK_INGREDIENTS


@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient_by_id(ingredient_id: int):
    """
    Retrieve a specific ingredient by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'products_list'.
    """
    for ingredient in MOCK_INGREDIENTS:
        if ingredient["id"] == ingredient_id:
            return ingredient
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ingredient not found"
    )


@router.post("/", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def create_ingredient(ingredient: IngredientCreate):
    """
    Create a new ingredient in the inventory.
    
    UI Note: On successful creation, the frontend should show a success toast 
    and redirect the user to 'products_list'.
    """
    if is_name_duplicated(ingredient.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with name '{ingredient.name}' already exists."
            )

    new_id = max(i["id"] for i in MOCK_INGREDIENTS) + 1 if MOCK_INGREDIENTS else 1
    new_ingredient = ingredient.model_dump() # convert model to dict
    new_ingredient["id"] = new_id

    MOCK_INGREDIENTS.append(new_ingredient)

    return new_ingredient


@router.patch("/{ingredient_id}", response_model=IngredientResponse, status_code=status.HTTP_200_OK)
async def update_ingredient(ingredient_id: int, ingredient: IngredientUpdate):
    """
    Partially update an existing ingredient in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'products_list' route.
    """
    target = None
    for i in MOCK_INGREDIENTS:
        if i["id"] == ingredient_id:
            target = i
            break
        
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id '{ingredient_id}' not found"
        )
    
    if ingredient.name is not None:
        if is_name_duplicated(ingredient.name, ingredient_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient with name '{ingredient.name}' already exists."
                )
    
    update_data = ingredient.model_dump(exclude_unset=True)  # get explicit values and ignore nulls
    target.update(update_data)

    return target


@router.delete("/{ingredient_id}", status_code=status.HTTP_200_OK)
async def delete_ingredient(ingredient_id: int):
    """
    Delete an ingredient from the inventory.
    
    UI Note: On successful deletion (204), remove the item from the local 
    state or refetch the list, and ensure the user is on 'products_list'.
    """
    for i in MOCK_INGREDIENTS:
        if i["id"] == ingredient_id:
            MOCK_INGREDIENTS.remove(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Ingredient with id '{ingredient_id}' not found"
    )