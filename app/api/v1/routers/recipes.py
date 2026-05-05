
from fastapi import APIRouter, HTTPException, status
from app.schemas.recipe import RecipeResponse, RecipeCreate, RecipeUpdate
from typing import Optional

# temp
from .ingredients import MOCK_INGREDIENTS


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


def is_recipe_duplicated(name: str, exclude_id: Optional[int] = None) -> bool:
    for recipe in MOCK_RECIPES:
        if recipe["name"].lower() == name.lower() and recipe["id"] != exclude_id:
            return True
    return False


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


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate):
    """
    Create a new recipe in the inventory.
    
    UI Note: On successful creation, the frontend should show a success toast 
    and redirect the user to 'recipes_list'.
    """
    if is_recipe_duplicated(recipe.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe with name '{recipe.name}' already exists."
        )
    
    max_id = max(r["id"] for r in MOCK_RECIPES) + 1 if MOCK_RECIPES else 1
    new_recipe = recipe.model_dump()  # convert model to dict
    new_recipe["id"] = max_id

    for ingredient in new_recipe["ingredients"]:
        found = False
        for i in MOCK_INGREDIENTS:
            if i["id"] == ingredient["ingredient_id"]:
                ingredient["ingredient_name"] = i["name"]
                ingredient["ingredient_unit"] = i["unit"]
                found = True
                break

        if not found:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with ID {ingredient["ingredient_id"]} not found."
        )
        
    MOCK_RECIPES.append(new_recipe)

    return new_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int):
    """
    Delete a recipe from the inventory.
    
    UI Note: On successful deletion (204), remove the item from the local 
    state or refetch the list, and ensure the user is on 'recipes_list'.
    """
    for recipe in MOCK_RECIPES:
        if recipe["id"] == recipe_id:
            recipe["is_active"] = False
            return
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Recipe with id {recipe_id} not found."
    )


@router.patch("/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
async def update_recipe(recipe_id: int, recipe_in: RecipeUpdate):
    """
    Partially update an existing recipe in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'recipes_list' route.
    """
    target = None
    for recipe in MOCK_RECIPES:
        if recipe["id"] == recipe_id:
            target = recipe
            break
        
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id '{recipe_id}' not found"
        )
    
    if recipe_in.name is not None:
        if is_recipe_duplicated(recipe_in.name, recipe_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recipe with name '{recipe_in.name}' already exists."
            )
        
    updated_data = recipe_in.model_dump(exclude_unset=True)  # get explicit values and ignore nulls
    
    if "ingredients" in updated_data:
        for ingredient_dict in updated_data["ingredients"]:
            found = False
            for i in MOCK_INGREDIENTS:
                if i["id"] == ingredient_dict["ingredient_id"]:
                    ingredient_dict["ingredient_name"] = i["name"]
                    ingredient_dict["ingredient_unit"] = i["unit"]
                    found = True
                    break

            if not found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with ID {ingredient_dict['ingredient_id']} not found."
                )
    
    target.update(updated_data)

    return target
