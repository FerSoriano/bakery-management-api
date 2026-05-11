
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate

class IngredientService:
    """
    Handles all business logic and database operations for Ingredients.
    """

    @staticmethod
    async def get_all(db: AsyncSession, include_inactive: bool = False):
        """
        Retrieve ingredients. Filters out inactive ones unless explicitly requested.
        """
        query = select(Ingredient)
        
        if not include_inactive:
            query = query.where(Ingredient.is_active == True)

        result = await db.execute(query)
        
        return result.scalars().all()


    @staticmethod
    async def get_by_id(db: AsyncSession, ingredient_id: int, include_inactive: bool = False):
        """
        Retrieve a single active ingredient by its ID.
        """
        query = select(Ingredient).where(Ingredient.id == ingredient_id)

        if not include_inactive:
            query = query.where(Ingredient.is_active == True)

        result = await db.execute(query)
        
        # scalar_one_or_none() returns the object if found, or None if it doesn't exist
        return result.scalar_one_or_none()
    

    @staticmethod
    async def get_by_name(db: AsyncSession, ingredient_name: str):
        """
        Retrieve a single active ingredient by its Name.
        """
        query = select(Ingredient).where(
            Ingredient.name.ilike(ingredient_name),
            Ingredient.is_active == True
        )
        result = await db.execute(query)

        return result.scalar_one_or_none()


    @staticmethod
    async def create(db: AsyncSession, ingredient_in: IngredientCreate):
        """
        Insert a new ingredient into the database.
        """
        # Convert the Pydantic schema to a dictionary and unpack it into the SQLAlchemy model
        new_ingredient = Ingredient(**ingredient_in.model_dump())
        
        db.add(new_ingredient)
        await db.commit()
        
        # Refresh to get the auto-generated ID and default values (like created_at)
        await db.refresh(new_ingredient)
        
        return new_ingredient
    

    @staticmethod
    async def update(db: AsyncSession, db_ingredient: Ingredient, update_data: dict):
        """
        Update an existing ingredient. 
        Expects the database object and a dictionary of the updated fields.
        """
        for key, value in update_data.items():
            setattr(db_ingredient, key, value)
            
        await db.commit()
        await db.refresh(db_ingredient)
        
        return db_ingredient


    @staticmethod
    async def delete(db: AsyncSession, db_ingredient: Ingredient):
        """
        Perform a soft delete by setting is_active to False.
        This preserves historical data for recipes that might have used this ingredient.
        """
        db_ingredient.is_active = False
        await db.commit()
        
        return