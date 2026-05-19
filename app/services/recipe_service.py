from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient

from app.schemas.recipe import RecipeCreate


class RecipeService:
    """
    Handles all business logic and database operations for Recipes.
    """
    @staticmethod
    async def get_all(db: AsyncSession, include_inactive: bool = False):
        """
        Retrieves all recipes, including its nested ingredients.
        """
        query = (
            select(Recipe)
            .options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
            )
        )
        
        if not include_inactive:
            query = query.where(Recipe.is_active == True)
            
        result = await db.execute(query)
        return result.unique().scalars().all()
    

    @staticmethod
    async def get_by_id(
        db: AsyncSession, 
        recipe_id: int,
        include_inactive: bool = False
    ) -> Recipe | None:
        """
        Retrieves a single recipe by its id, including its nested ingredients.
        """
        query = (
            select(Recipe)
            .options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
            )
            .where(Recipe.id == recipe_id)
        )

        if not include_inactive:
            query = query.where(Recipe.is_active == True)

        result = await db.execute(query)
        return result.unique().scalars().first()
    

    @staticmethod
    async def get_by_name(db: AsyncSession, recipe_name: str) -> Recipe | None:
        """
        Retrieves a single recipe by its name, including its nested ingredients.
        """
        query = (
            select(Recipe)
            .options(
                joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
            )
            .where(Recipe.name.ilike(recipe_name))
        )
        result = await db.execute(query)
        return result.unique().scalars().first()
    

    @staticmethod
    async def create(
        db: AsyncSession,
        recipe_in: RecipeCreate
    ) -> Recipe:
        """
        Insert a new Recipe into the database.
        """
        new_recipe = Recipe(
            name=recipe_in.name,
            description=recipe_in.description,
            is_active=recipe_in.is_active
        )

        for ingredient in recipe_in.ingredients:
            recipe_ingredient = RecipeIngredient (
                ingredient_id=ingredient.ingredient_id,
                quantity=ingredient.quantity
            )
            new_recipe.ingredients.append(recipe_ingredient)
        
        db.add(new_recipe)

        await db.commit()
        
        # We perform a re-query instead of just returning new_recipe because 
        # we need to eagerly load the nested ingredients relationship (joinedload) 
        # to fulfill the Pydantic response schema without throwing a MissingGreenlet error.
        return await RecipeService.get_by_id(db, new_recipe.id)  # type: ignore
    

    @staticmethod
    async def update(
        db: AsyncSession,
        db_recipe: Recipe,
        update_data: dict
    ) -> Recipe:
        """
        Update an existing recipe and its ingredients.
        """
        ingredients_data = update_data.pop("ingredients", None)

        for key, value in update_data.items():
            setattr(db_recipe, key, value)

        if ingredients_data is not None:
            db_recipe.ingredients.clear()

            for item in ingredients_data:
                recipe_ingredient = RecipeIngredient(
                    ingredient_id=item["ingredient_id"],
                    quantity=item["quantity"]
                )
                db_recipe.ingredients.append(recipe_ingredient)
                
        await db.commit()
            
        return await RecipeService.get_by_id(db, db_recipe.id)  # type: ignore
    

    @staticmethod
    async def delete(db: AsyncSession, db_recipe: Recipe):
        """
        Perform a soft delete by setting is_active to False.
        """
        db_recipe.is_active = False  # type: ignore
        await db.commit()
        return