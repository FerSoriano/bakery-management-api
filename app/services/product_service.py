from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.product import ProductCreate


class ProductService:
    """
    Handles all business logic and database operations for Products.
    """

    @staticmethod
    async def _get_recipe_costs(db: AsyncSession, recipe_ids: list[int]) -> dict[int, float]:
        if not recipe_ids:
            return {}

        query = (
            select(
                RecipeIngredient.recipe_id,
                func.coalesce(
                    func.sum(RecipeIngredient.quantity * Ingredient.current_unit_price),
                    0.0
                ),
            )
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .where(RecipeIngredient.recipe_id.in_(recipe_ids))
            .group_by(RecipeIngredient.recipe_id)
        )

        result = await db.execute(query)
        return {recipe_id: float(cost or 0.0) for recipe_id, cost in result.all()}


    @staticmethod
    async def get_all(db: AsyncSession, include_inactive: bool = False):
        """
        Retrieve products. Filters out inactive ones unless explicitly requested.
        """
        query = select(Product)

        if not include_inactive:
            query = query.where(Product.is_active == True)

        result = await db.execute(query)
        products = result.scalars().all()
        recipe_ids = [product.recipe_id for product in products if product.recipe_id is not None]
        costs = await ProductService._get_recipe_costs(db, recipe_ids)  # type: ignore

        for product in products:
            product.cost = costs.get(product.recipe_id, 0.0)  # type: ignore[attr-defined]

        return products
    

    @staticmethod
    async def get_by_id(
        db: AsyncSession, 
        product_id: int, 
        include_inactive: bool = False
    )  -> Product | None:
        """
        Retrieve a single active product by its ID.
        """
        query = select(Product).where(Product.id == product_id)

        if not include_inactive:
            query = query.where(Product.is_active == True)

        result = await db.execute(query)
        product = result.scalar_one_or_none()

        if product is None:
            return None

        costs = await ProductService._get_recipe_costs(db, [product.recipe_id])  # type: ignore
        product.cost = costs.get(product.recipe_id, 0.0)  # type: ignore[attr-defined]

        return product
    

    @staticmethod
    async def get_by_name(db: AsyncSession, product_name: str) -> Product | None:
        """
        Retrieve a single active product by its Name.
        """
        query = select(Product).where(Product.name == product_name)

        result = await db.execute(query)
        product = result.scalar_one_or_none()

        if product is None:
            return None

        costs = await ProductService._get_recipe_costs(db, [product.recipe_id])  # type: ignore
        product.cost = costs.get(product.recipe_id, 0.0)  # type: ignore[attr-defined]

        return product
    

    @staticmethod
    async def create(db: AsyncSession, product_in: ProductCreate):
        """
        Insert a new product into the database.
        """
        new_product = Product(**product_in.model_dump())

        db.add(new_product)
        await db.commit()

        await db.refresh(new_product)
        costs = await ProductService._get_recipe_costs(db, [new_product.recipe_id])  # type: ignore
        new_product.cost = costs.get(new_product.recipe_id, 0.0)  # type: ignore[attr-defined]

        return new_product
    
    
    @staticmethod
    async def update(db: AsyncSession, db_product: Product, update_data: dict):
        """
        Update an existing product. 
        Expects the database object and a dictionary of the updated fields.
        """
        for key, value in update_data.items():
            setattr(db_product, key, value)
            
        await db.commit()
        await db.refresh(db_product)
        costs = await ProductService._get_recipe_costs(db, [db_product.recipe_id])  # type: ignore
        db_product.cost = costs.get(db_product.recipe_id, 0.0)  # type: ignore[attr-defined]
        
        return db_product
    

    @staticmethod
    async def delete(db: AsyncSession, db_product: Product):
        """
        Perform a soft delete by setting is_active to False.
        This preserves historical data for recipes that might have used this product.
        """
        db_product.is_active = False  # type: ignore
        await db.commit()
        
        return
