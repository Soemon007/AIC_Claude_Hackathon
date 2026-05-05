from pydantic import BaseModel, Field
from typing import List, Optional

class User(BaseModel):
    username: str
    age: int
    weight: float

class MealRequest(BaseModel):
    profile: User
    ingredients: List[str] = Field(..., description="List of raw ingredients provided by user")
    meal_type: str = Field(..., description="e.g., Breakfast, Lunch, Dinner")
    #options for the meal type to be given in the frontend could be Breakfast, Lunch, Dinner, Snack.

class MealResponse(BaseModel):
    meal_name: str
    why_this_works: List[str] = Field(..., description="Bullet points on why this fits PCOS guidelines")
    cautions: List[str] = Field(..., description="Warnings about portion sizes or specific ingredients")

