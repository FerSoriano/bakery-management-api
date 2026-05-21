from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from app.services.recipe_service import RecipeService
from app.db.database import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("/", response_model=list[ProductResponse])
async def get_products(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrive a list of all products
    """
    return await ProductService.get_all(db, include_inactive)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific product by its unique ID.
    
    UI Note: If this returns a 404, the frontend should display a 'Not Found' 
    message and provide a 'Back' or 'Cancel' button routing to 'products_list'.
    """
    db_product = await ProductService.get_by_id(db, product_id, include_inactive)
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found."
        )

    return db_product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product and link it to an existing recipe.
    
    UI Note: On successful creation (201), redirect the user to 'products_list' 
    or clear the form for a new entry.
    """
    db_product = await ProductService.get_by_name(db, product_in.name)
    if db_product is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with name '{product_in.name}' already exists."
        )
    
    # validate if recipe id exists
    db_recipe = await RecipeService.get_by_id(db, product_in.recipe_id)
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot link product to recipe. Recipe with id {product_in.recipe_id} does not exist."
        )

    return await ProductService.create(db, product_in)


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int, 
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update an existing Product in the inventory.
    
    UI Note: On successful update or if the user clicks 'Cancel', 
    the frontend should redirect to the 'products_list' route.
    """
    db_product = await ProductService.get_by_id(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found"
        )

    if product_in.name is not None and product_in.name != db_product.name:
        existing_name = await ProductService.get_by_name(db, product_in.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with name '{product_in.name}' already exists."
            )
    
    updated_data = product_in.model_dump(exclude_unset=True)

    if product_in.recipe_id is not None:
        db_recipe = await RecipeService.get_by_id(db, product_in.recipe_id)
        if not db_recipe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot link product to recipe. Recipe with id {product_in.recipe_id} does not exist."
            )

    return await ProductService.update(db, db_product, updated_data)


@router.patch("/{product_id}/reactivate", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def reactivate_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_product = await ProductService.get_by_id(db, product_id, include_inactive=True)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id '{product_id}' not found"
        )
    
    update_data = product_in.model_dump(exclude_unset=True)
    update_data["is_active"] = True

    return await ProductService.update(db, db_product, update_data) 



@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a product from the inventory.
    
    UI Note: On successful deletion (204), remove the item from the local 
    state or refetch the list, and ensure the user is on 'products_list'.
    """
    db_product = await ProductService.get_by_id(db, product_id)

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    return await ProductService.delete(db, db_product)