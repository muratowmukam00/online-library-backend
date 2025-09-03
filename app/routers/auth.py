import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "password")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(or_(User.username == user.username, User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail='Username or email already registered')

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

