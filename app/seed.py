import asyncio
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.db.database import AsyncSessionLocal
from app.services.ingredient_service import IngredientService
from app.services.recipe_service import RecipeService
from app.schemas.ingredient import IngredientCreate
from app.schemas.recipe import RecipeCreate, RecipeIngredientCreate

async def get_or_create_ingredient(db, ingredient_in: IngredientCreate):
    existing = await IngredientService.get_by_name(db, ingredient_in.name)
    if existing:
        return existing
    return await IngredientService.create(db, ingredient_in)

async def get_or_create_recipe(db, recipe_in: RecipeCreate):
    existing = await RecipeService.get_by_name(db, recipe_in.name)
    if existing:
        return existing
    return await RecipeService.create(db, recipe_in)

async def populate_database():
    print("🚀 Starting database seeding...")
    
    async with AsyncSessionLocal() as db:
        try:
            print("📦 Inserting ingredients...")
            
            harina_in = IngredientCreate(
                name="Harina de Trigo",
                stock_quantity=12.0,
                unit="kg",  # type: ignore
                category="secos",  # type: ignore
                current_unit_price=25.50,
            )
            mantequilla_in = IngredientCreate(
                name="Mantequilla",
                stock_quantity=5.0,
                unit="kg",  # type: ignore
                category="lacteos",  # type: ignore
                current_unit_price=92.00,
            )
            azucar_in = IngredientCreate(
                name="Azúcar Refinada",
                stock_quantity=10.0,
                unit="kg",  # type: ignore
                category="secos",  # type: ignore
                current_unit_price=22.00,
            )
            leche_in = IngredientCreate(
                name="Leche Entera",
                stock_quantity=25.0,
                unit="l",  # type: ignore
                category="lacteos",  # type: ignore
                current_unit_price=14.50,
            )
            huevos_in = IngredientCreate(
                name="Huevo",
                stock_quantity=48.0,
                unit="pza",  # type: ignore
                category="secos",  # type: ignore
                current_unit_price=3.50,
            )

            db_harina = await get_or_create_ingredient(db, harina_in)
            db_mantequilla = await get_or_create_ingredient(db, mantequilla_in)
            db_azucar = await get_or_create_ingredient(db, azucar_in)
            db_leche = await get_or_create_ingredient(db, leche_in)
            db_huevos = await get_or_create_ingredient(db, huevos_in)
            
            print("✅ Ingredients inserted successfully.")

            print("🥣 Inserting recipes...")

            croissant_in = RecipeCreate(
                name="Croissant de Mantequilla",
                instructions="Mezclar harina, leche y azúcar. Amasar y dejar fermentar. Laminar con la mantequilla fría dando 3 pliegues. Hornear a 190°C por 22 minutos.",
                ingredients=[
                    RecipeIngredientCreate(ingredient_id=db_harina.id, quantity=0.500),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_mantequilla.id, quantity=0.250),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_leche.id, quantity=0.300),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_azucar.id, quantity=0.060)  # type: ignore
                ]
            )
            
            pan_caja_in = RecipeCreate(
                name="Pan de Caja Artesanal",
                instructions="Mezclar ingredientes, amasar hasta desarrollar ventana. Fermentación en bloque de 1 hora. Formar en molde y hornear a 200°C por 35 minutos.",
                ingredients=[
                    RecipeIngredientCreate(ingredient_id=db_harina.id, quantity=0.600),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_leche.id, quantity=0.350),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_azucar.id, quantity=0.030),  # type: ignore
                    RecipeIngredientCreate(ingredient_id=db_huevos.id, quantity=2.0)  # type: ignore
                ]
            )

            await get_or_create_recipe(db, croissant_in)
            await get_or_create_recipe(db, pan_caja_in)
            
            print("✅ Recipes inserted successfully.")
            print("🎉 Database seeding completed successfully!")

        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(populate_database())