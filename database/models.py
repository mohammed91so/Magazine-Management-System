"""
Database models for the inventory system.

This module defines the data models for products and sales,
providing type safety and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Represents a product in the inventory."""
    
    id: Optional[int] = None
    name: str = ""
    purchase_price: float = 0.0
    selling_price: float = 0.0
    quantity: int = 0
    expiration_date: str = ""
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "purchase_price": self.purchase_price,
            "selling_price": self.selling_price,
            "quantity": self.quantity,
            "expiration_date": self.expiration_date,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create product from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            purchase_price=data.get("purchase_price", 0.0),
            selling_price=data.get("selling_price", 0.0),
            quantity=data.get("quantity", 0),
            expiration_date=data.get("expiration_date", ""),
            created_at=data.get("created_at")
        )


@dataclass
class Sale:
    """Represents a sales transaction."""
    
    id: Optional[int] = None
    product_id: int = 0
    quantity: int = 0
    total_price: float = 0.0
    profit: float = 0.0
    date: Optional[str] = None
    product_name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert sale to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "profit": self.profit,
            "date": self.date,
            "product_name": self.product_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Sale":
        """Create sale from dictionary."""
        return cls(
            id=data.get("id"),
            product_id=data.get("product_id", 0),
            quantity=data.get("quantity", 0),
            total_price=data.get("total_price", 0.0),
            profit=data.get("profit", 0.0),
            date=data.get("date"),
            product_name=data.get("product_name")
        )
