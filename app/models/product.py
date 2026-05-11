from sqlalchemy import (
    Column,
    Integer, 
    String, 
    Float, 
    Boolean, 
    DateTime, 
    Enum, 
    ForeignKey
)
from sqlalchemy.sql import func
from app.db.database import Base
from app.schemas.product import ProductCategory


class Product(Base):
    """
    SQLAlchemy model for the 'products' table.
    Represents the final items sold in the bakery.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    sale_price = Column(Float, default=0.0)

    category = Column(Enum(ProductCategory), nullable=False)

    recipe_id = Column(
        Integer, 
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )
    
    is_active = Column(Boolean, default=True)

    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<Product(name={self.name}, sale_price={self.sale_price})>"
