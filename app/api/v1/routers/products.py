from fastapi import APIRouter, HTTPException, status
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate

#temp
from .recipes import MOCK_RECIPES
from .ingredients import MOCK_INGREDIENTS


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


MOCK_PRODUCTS = [
    {
        "id": 1,
        "name": "Premium Chocolate Cake (Whole)",
        "description": "Our classic signature chocolate cake. Serves 10.",
        "sale_price": 450.00,
        "category": "Cakes",
        "recipe_id": 1, 
        "is_active": True
    },
    {
        "id": 2,
        "name": "Chocolate Cake Slice",
        "description": "A single slice of our signature chocolate cake.",
        "sale_price": 65.00,
        "category": "Slices",
        "recipe_id": 1, 
        "is_active": True
    },
    {
        "id": 3,
        "name": "Vanilla Eclair",
        "description": "Classic French pastry filled with our special vanilla pastry cream.",
        "sale_price": 45.00,
        "category": "Individual Desserts",
        "recipe_id": 2,
        "is_active": True
    }
]


def get_product_cost_by_recipe(recipe_id: int) -> float:
    """
    Calculates the total cost of a product based on its recipe ingredients.
    """
    recipe = next((r for r in MOCK_RECIPES if r["id"] == recipe_id), None)
    
    if not recipe:
        return 0.0

    price_index = {i["id"]: i.get("current_unit_price", 0.0) for i in MOCK_INGREDIENTS}

    total_cost = 0.0
    
    for recipe_ing in recipe.get("ingredients", []):
        ingredient_id = recipe_ing["ingredient_id"]
        unit_price = price_index.get(ingredient_id, 0.0) 
        total_cost += recipe_ing["quantity"] * unit_price

    return total_cost


@router.get("/", response_model=list[ProductResponse])
async def get_products():
    """
    Retrive a list of all ACTIVE products
    """
    active_products = [product for product in MOCK_PRODUCTS if product.get("is_active", True)]
    for product in active_products:
        product["cost"] = get_product_cost_by_recipe(product["recipe_id"])
    return active_products
