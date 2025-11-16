"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# Example schemas kept for reference
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Vacation rental app schemas

class Property(BaseModel):
    """
    Collection: "property"
    A vacation rental property (cabin, hut, lodge, etc.)
    """
    title: str
    description: str
    location: str
    country: Optional[str] = None
    price_per_night: float = Field(..., ge=0)
    max_guests: int = Field(..., ge=1)
    bedrooms: int = Field(1, ge=0)
    bathrooms: int = Field(1, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = 0
    amenities: List[str] = []
    image_urls: List[str] = []

class Booking(BaseModel):
    """
    Collection: "booking"
    A booking inquiry for a property
    """
    property_id: str
    name: str
    email: str
    phone: Optional[str] = None
    check_in: date
    check_out: date
    guests: int = Field(..., ge=1)
    message: Optional[str] = None
