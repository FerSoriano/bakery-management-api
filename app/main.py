
from fastapi import FastAPI
from app.api.v1.routers import ingredients


app = FastAPI(
    title="Bakery Management API",
    description="Backend system for bakery management",
    version="0.1.0"
)


# routers
app.include_router(ingredients.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    return {"msg": "Welcome to the Bakery API"}

