
from fastapi import APIRouter
from app.schemas.ingredient import IngredientResponse


router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

# Mock data
MOCK_INGREDIENTS = [
    {"id": 1, "name": "Flour", "stock_quantity": 50.0, "unit": "kg"},
    {"id": 2, "name": "Sugar", "stock_quantity": 20.0, "unit": "kg"},
    {"id": 3, "name": "Vanilla Extract", "stock_quantity": 2.5, "unit": "liters"},
]


@router.get("/", response_model=list[IngredientResponse])
async def get_ingredients():
    """
    Retrieve a list of all ingredients in the bakery's inventory.
    """
    return MOCK_INGREDIENTS