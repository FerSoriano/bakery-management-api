from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Ingredient(Base):
    """
    SQLAlchemy model for the 'ingredients' table.
    Defines the physical schema for raw materials in the inventory.
    """
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    stock_quantity = Column(Float, default=0.0)
    unit = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_unit_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Audit timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<Ingredient(name={self.name}, unit={self.unit})>"