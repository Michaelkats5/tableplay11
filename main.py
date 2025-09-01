import os
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import User, Restaurant, Favorite
from .schemas import UserCreate, UserOut, TokenOut, LoginIn, RestaurantOut, FavoriteIn, FavoriteOut
from .security import hash_password, verify_password, create_token, decode_token

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="TablePlay API", version="0.1.0")

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed minimal restaurants if empty
def seed(db: Session):
    if db.query(Restaurant).count() == 0:
        data = [
            dict(key='lp01', name='Luna Plant Kitchen', cuisine='Mediterranean', price='$$', rating=4.6, distance_km=1.1,
                 tags='Vegan,Nut-Free,Halal', badges='No Peanut Oil,Allergy-trained Staff',
                 menu_highlights='Falafel Bowl,Hummus Trio,Za’atar Flatbread'),
            dict(key='gg02', name='Grill & Grain', cuisine='American', price='$$', rating=4.3, distance_km=2.5,
                 tags='High-Protein,Keto-Friendly,Gluten-Free', badges='Cross-contact Protocols', menu_highlights='Chicken Bowl,Cauliflower Mash,Grass-fed Burger (lettuce wrap)'),
            dict(key='sh03', name='Soba House', cuisine='Japanese', price='$$', rating=4.7, distance_km=3.2,
                 tags='Dairy-Free,Pescatarian,Low-Sodium', badges='Soy Alternatives Available', menu_highlights='Cold Soba,Salmon Don,Tofu Miso Soup'),
        ]
        for d in data:
            r = Restaurant(**d)
            db.add(r)
        db.commit()

with SessionLocal() as _db:
    seed(_db)

def get_current_user(db: Session = Depends(get_db), authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    sub = decode_token(token)
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.post("/auth/register", response_model=TokenOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, display_name=payload.display_name, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    token = create_token(sub=user.email)
    return TokenOut(access_token=token)

@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(sub=user.email)
    return TokenOut(access_token=token)

@app.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@app.get("/restaurants", response_model=list[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db)):
    rows = db.query(Restaurant).all()
    out = []
    for r in rows:
        out.append(RestaurantOut(
            id=r.id, key=r.key, name=r.name, cuisine=r.cuisine, price=r.price, rating=r.rating,
            distance_km=r.distance_km,
            tags=[t.strip() for t in r.tags.split(",") if t.strip()],
            badges=[t.strip() for t in r.badges.split(",") if t.strip()],
            menu_highlights=[t.strip() for t in r.menu_highlights.split(",") if t.strip()],
        ))
    return out

@app.get("/favorites", response_model=list[RestaurantOut])
def get_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = db.query(Favorite).filter(Favorite.user_id == user.id).all()
    out = []
    for f in favs:
        r = f.restaurant
        out.append(RestaurantOut(
            id=r.id, key=r.key, name=r.name, cuisine=r.cuisine, price=r.price, rating=r.rating,
            distance_km=r.distance_km,
            tags=[t.strip() for t in r.tags.split(",") if t.strip()],
            badges=[t.strip() for t in r.badges.split(",") if t.strip()],
            menu_highlights=[t.strip() for t in r.menu_highlights.split(",") if t.strip()],
        ))
    return out

@app.post("/favorites", response_model=RestaurantOut)
def add_favorite(payload: FavoriteIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.get(Restaurant, payload.restaurant_id)
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    existing = db.query(Favorite).filter(Favorite.user_id==user.id, Favorite.restaurant_id==r.id).first()
    if not existing:
        db.add(Favorite(user_id=user.id, restaurant_id=r.id))
        db.commit()
    return RestaurantOut(
        id=r.id, key=r.key, name=r.name, cuisine=r.cuisine, price=r.price, rating=r.rating,
        distance_km=r.distance_km,
        tags=[t.strip() for t in r.tags.split(",") if t.strip()],
        badges=[t.strip() for t in r.badges.split(",") if t.strip()],
        menu_highlights=[t.strip() for t in r.menu_highlights.split(",") if t.strip()],
    )

@app.delete("/favorites/{restaurant_id}")
def remove_favorite(restaurant_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.user_id==user.id, Favorite.restaurant_id==restaurant_id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"ok": True}
