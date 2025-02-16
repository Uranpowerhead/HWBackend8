from fastapi import FastAPI, Form, HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
import jwt
import time

DATABASE_URL = "sqlite:///./flowers.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = "supersecretkey"

app = FastAPI()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)


class FlowerDB(Base):
    __tablename__ = "flowers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)

class PurchaseDB(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey("users.email"))
    flower_id = Column(Integer, ForeignKey("flowers.id"))

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_jwt(email: str) -> str:
    payload = {"email": email, "exp": time.time() + 3600}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Сессия истекла")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неправильный token")

@app.post("/signup")
async def signup(email: str = Form(), name: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = UserDB(email=email, name=name, password=password)
    db.add(user)
    db.commit()
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/login")
async def login(email: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == email, UserDB.password == password).first()
    if not user:
        raise HTTPException(status_code=400, detail="Неправильные данные")
    token = create_jwt(email)
    return {"access_token": token, "type": "bearer"}

@app.get("/profile")
async def profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = decode_jwt(token)
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"email": user.email, "name": user.name}

@app.get("/flowers")
async def get_flowers(db: Session = Depends(get_db)):
    return db.query(FlowerDB).all()

@app.post("/flowers")
async def add_flower(name: str = Form(), price: float = Form(), db: Session = Depends(get_db)):
    flower = FlowerDB(name=name, price=price)
    db.add(flower)
    db.commit()
    return {"id": flower.id}

@app.patch("/flowers/{flower_id}")
async def update_flower(flower_id: int, name: Optional[str] = Form(None), price: Optional[float] = Form(None), db: Session = Depends(get_db)):
    flower = db.query(FlowerDB).filter(FlowerDB.id == flower_id).first()
    if not flower:
        raise HTTPException(status_code=404, detail="Цветок не найден")
    if name:
        flower.name = name
    if price:
        flower.price = price
    db.commit()
    return {"message": "Цветок обновлен"}

@app.delete("/flowers/{flower_id}")
async def delete_flower(flower_id: int, db: Session = Depends(get_db)):
    flower = db.query(FlowerDB).filter(FlowerDB.id == flower_id).first()
    if not flower:
        raise HTTPException(status_code=404, detail="Цветок не найден")
    db.delete(flower)
    db.commit()
    return {"message": "Цветок удален"}

@app.post("/purchased")
async def purchase(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = decode_jwt(token)
    purchase = PurchaseDB(user_email=email, flower_id=1)
    db.add(purchase)
    db.commit()
    return {"message": "Покупка совершенна"}

@app.get("/purchased")
async def view_purchases(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = decode_jwt(token)
    user_purchases = db.query(PurchaseDB).filter(PurchaseDB.user_email == email).all()
    return {"purchased_flowers": user_purchases}
