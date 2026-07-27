
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import ingredients, recipes, products, health

from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.database import engine, Base


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

# CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], 
    allow_headers=['*']
)


# routers
app.include_router(health.router) 
app.include_router(ingredients.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    return {"msg": "Welcome to the Bakery API"}

