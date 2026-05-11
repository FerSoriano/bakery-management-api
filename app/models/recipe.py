
from sqlalchemy import (
    Column, 
    Integer,
    String, 
    Boolean, 
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Recipe(Base):
    """
    Physical table for Recipes.
    Acts as the parent container for a list of RecipeIngredients.
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recipe(name={self.name})>"
