from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class RestaurantOut(BaseModel):
    id: int
    key: str
    name: str
    cuisine: str
    price: str
    rating: float
    distance_km: float
    tags: List[str] = []
    badges: List[str] = []
    menu_highlights: List[str] = []
    class Config:
        from_attributes = True

class FavoriteIn(BaseModel):
    restaurant_id: int

class FavoriteOut(BaseModel):
    restaurant: RestaurantOut
    class Config:
        from_attributes = True
