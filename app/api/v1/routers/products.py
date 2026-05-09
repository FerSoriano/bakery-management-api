from fastapi import APIRouter, HTTPException, status
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from typing import Optional

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


def is_product_duplicated(product_name: str, exclude_id: Optional[int] = None) -> bool:
    """
    Check if a product name already exists in the mock database.
    Case-insensitive. Optionally excludes a specific ID (useful for updates).
    """
    for product in MOCK_PRODUCTS:
        if product["name"].lower() == product_name.lower() and product["id"] != exclude_id:
            return True
    return False


def recipe_exists(recipe_id: int) -> bool:
    return any(recipe["id"] == recipe_id for recipe in MOCK_RECIPES)


@router.get("/", response_model=list[ProductResponse])
async def get_products():
    """
    Retrive a list of all ACTIVE products
    """
    active_products = [product for product in MOCK_PRODUCTS if product.get("is_active", True)]
    for product in active_products:
        product["cost"] = get_product_cost_by_recipe(product["recipe_id"])
    return active_products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: int):
    """
    Retrieve a specific product by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'products_list'.
    """
    for product in MOCK_PRODUCTS:
        if product["id"] == product_id and product.get("is_active", True):
            product["cost"] = get_product_cost_by_recipe(product["recipe_id"])
            return product
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with id '{product_id}' not found."
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate):
    """
    Create a new product and link it to an existing recipe.
    
    UI Note: On successful creation (201), redirect the user to 'products_list' 
    or clear the form for a new entry.
    """
    if is_product_duplicated(product_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with name '{product_in.name}' already exists."
        )
    
    if not recipe_exists(product_in.recipe_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot link product to recipe. Recipe with id {product_in.recipe_id} does not exist."
        )

    new_id = max(p["id"] for p in MOCK_PRODUCTS) + 1 if MOCK_PRODUCTS else 1
    
    new_product = product_in.model_dump()
    new_product["id"] = new_id
    new_product["cost"] = get_product_cost_by_recipe(new_product["recipe_id"])

    MOCK_PRODUCTS.append(new_product)

    return new_product


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product_in: ProductUpdate):
    """
    Partially update an existing Product in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'products_list' route.
    """
    target = None
    for product in MOCK_PRODUCTS:
        if product["id"] == product_id:
            target = product
            break

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found"
        )

    if product_in.name is not None:
        if is_product_duplicated(product_in.name, product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{product_in.name}' already exists."
            )
    
    updated_data = product_in.model_dump(exclude_unset=True)

    if product_in.recipe_id is not None:
        if not recipe_exists(product_in.recipe_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot link product to recipe. Recipe with id {product_in.recipe_id} does not exist."
            )
    
    target.update(updated_data)

    target["cost"] = get_product_cost_by_recipe(target["recipe_id"])
        
    return target
        