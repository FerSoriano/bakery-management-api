
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.recipe import RecipeResponse, RecipeCreate, RecipeUpdate
from app.services.recipe_service import RecipeService
from app.services.ingredient_service import IngredientService
from app.db.database import get_db



router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)


@router.get("/", response_model=list[RecipeResponse])
async def get_recipes(
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = False
):
    """
    Retrieve a list of all ACTIVE recipes.
    """
    return await RecipeService.get_all(db, include_inactive)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_by_id(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = False
):
    """
    Retrieve a specific recipe by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'recipes_list'.
    """
    db_recipe = await RecipeService.get_by_id(db, recipe_id, include_inactive)
    
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id '{recipe_id}' not found"
        )

    return db_recipe


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_in: RecipeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new recipe in the inventory.
    
    UI Note: On successful creation, the frontend should show a success toast 
    and redirect the user to 'recipes_list'.
    """
    db_recipe = await RecipeService.get_by_name(db, recipe_in.name)
    
    if db_recipe is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe with name '{recipe_in.name}' already exists."
        )
    
    requested_ids = {item.ingredient_id for item in recipe_in.ingredients}

    db_ingredients = await IngredientService.get_multiple_by_ids(db, list(requested_ids))
    found_ids = {ing.id for ing in db_ingredients}
    
    missing_ids = requested_ids - found_ids  # type: ignore
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredients with IDs {list(missing_ids)} not found or inactive."
        )
    
    return await RecipeService.create(db, recipe_in)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a recipe from the inventory.
    
    UI Note: On successful deletion (204), remove the item from the local 
    state or refetch the list, and ensure the user is on 'recipes_list'.
    """
    db_recipe = await RecipeService.get_by_id(db, recipe_id)
    
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found."
        )

    return await RecipeService.delete(db, db_recipe)


@router.patch("/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
async def update_recipe(
    recipe_id: int, 
    recipe_in: RecipeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update an existing recipe in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'recipes_list' route.
    """
    db_recipe = await RecipeService.get_by_id(db, recipe_id)
    
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found."
        )
    
    if recipe_in.name is not None and recipe_in.name != db_recipe.name:
        existing_name = await RecipeService.get_by_name(db, recipe_in.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recipe with name '{recipe_in.name}' already exists."
            )
    
    if recipe_in.ingredients is not None:
        requested_ids = {item.ingredient_id for item in recipe_in.ingredients}

        db_ingredients = await IngredientService.get_multiple_by_ids(db, list(requested_ids))
        found_ids = {ing.id for ing in db_ingredients}
        
        missing_ids = requested_ids - found_ids  # type: ignore
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredients with IDs {list(missing_ids)} not found or inactive."
            )

    update_data = recipe_in.model_dump(exclude_unset=True)  # get explicit values and ignore nulls
    updated_recipe = await RecipeService.update(db, db_recipe, update_data)

    return updated_recipe

@router.patch("/{recipe_id}/reactivate", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
async def reactivate_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate a previously deleted recipe.
    """
    db_recipe = await RecipeService.get_by_id(db, recipe_id, True)

    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found."
        )

    update_data = recipe_in.model_dump(exclude_unset=True)
    update_data["is_active"] = True

    return await RecipeService.update(db, db_recipe, update_data)
