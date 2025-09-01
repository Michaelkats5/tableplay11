from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True) # e.g., 'lp01'
    name = Column(String, nullable=False)
    cuisine = Column(String, nullable=False)
    price = Column(String, nullable=False) # $, $$, $$$
    rating = Column(Float, default=0.0)
    distance_km = Column(Float, default=0.0)
    tags = Column(String, default="")   # comma-separated
    badges = Column(String, default="") # comma-separated
    menu_highlights = Column(String, default="") # comma-separated

    favorites = relationship("Favorite", back_populates="restaurant", cascade="all, delete-orphan")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    restaurant = relationship("Restaurant", back_populates="favorites")

    __table_args__ = (UniqueConstraint('user_id', 'restaurant_id', name='_user_restaurant_uc'),)
