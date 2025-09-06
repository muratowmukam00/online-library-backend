import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import  verify_password, create_access_token
from app.schemas.token import Token
from app.core.database import get_db

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "password")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(tags=["auth"])



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


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # noinspection PyTypeChecker
    user: Optional[User] = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}