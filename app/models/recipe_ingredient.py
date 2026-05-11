
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class RecipeIngredient(Base):
    """
    Association table between Recipes and Ingredients.
    Stores the specific quantity of an ingredient needed for a recipe.
    """
    __tablename__ = "recipe_ingredient"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False
    )
    quantity = Column(Float, nullable=False)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Logical relationships - ORM
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient")

    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, quantity={self.quantity})>"
