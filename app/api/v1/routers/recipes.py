
from fastapi import APIRouter, HTTPException, status
from app.schemas.recipe import RecipeResponse, RecipeCreate


router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

MOCK_RECIPES = [
    {
        "id": 1,
        "name": "Classic Chocolate Cake",
        "description": "Rich and fluffy chocolate cake. Yields 10 slices.",
        "is_active": True,
        "ingredients": [
            {
                "ingredient_id": 1,
                "quantity": 0.5,
                "ingredient_name": "Flour",
                "ingredient_unit": "kg"
            },
            {
                "ingredient_id": 2,
                "quantity": 0.3,
                "ingredient_name": "Sugar",
                "ingredient_unit": "kg"
            }
        ]
    },
    {
        "id": 2,
        "name": "Vanilla Pastry Cream",
        "description": "Base cream for filling tarts and eclairs.",
        "is_active": True,
        "ingredients": [
            {
                "ingredient_id": 3,
                "quantity": 1.0,
                "ingredient_name": "Vanilla Extract",
                "ingredient_unit": "liters"
            },
            {
                "ingredient_id": 2,
                "quantity": 0.15,
                "ingredient_name": "Sugar",
                "ingredient_unit": "kg"
            }
        ]
    }
]


@router.get("/", response_model=list[RecipeResponse])
async def get_recipes():
    """
    Retrieve a list of all ACTIVE recipes.
    """
    active_recipes = [recipe for recipe in MOCK_RECIPES if recipe.get("is_active", True)]
    return active_recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_by_id(recipe_id: int):
    """
    Retrieve a specific recipe by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'recipes_list'.
    """
    for recipe in MOCK_RECIPES:
        if recipe.get("is_active", True) and recipe["id"] == recipe_id:
            return recipe
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Recipe with id '{recipe_id}' not found"
    )
