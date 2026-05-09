
from fastapi import FastAPI
from app.api.v1.routers import ingredients, recipes, products

from contextlib import asynccontextmanager
from app.db.database import engine, Base
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code executed before the application starts taking requests.
    """

    # dev environment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)    
    yield 
    
    await engine.dispose()


app = FastAPI(
    title="Bakery Management API",
    description="Backend system for bakery management",
    version="0.1.0",
    lifespan=lifespan
)


# routers
app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    return {"msg": "Welcome to the Bakery API"}

