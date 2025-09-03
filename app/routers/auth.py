from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import get_current_user

from app.schemas.token import Token, RefreshToken
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_tokens,
    refresh_user_token,
    logout_user,
    get_user_by_username_or_email
)


router = APIRouter(tags=["auth"])



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user in the system."""

    if get_user_by_username_or_email(db, user_data.username, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_user = register_user(db=db, user_data=user_data)
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user and returns access and refresh tokens."""

    user: Optional[User] = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return create_user_tokens(db=db, user=user)


@router.post("/refresh")
def refresh_token(token_data: RefreshToken, db: Session = Depends(get_db)):
    """Refreshes the access token using a valid refresh token."""

    new_access_token = refresh_user_token(db=db, refresh_token=token_data.refresh_token)
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token !",
        )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
        db: Session = Depends(get_db),
        current_user: Session = Depends(get_current_user)
):
    """Logs out the current user by invalidating their refresh token."""
    logout_user(db=db, current_user=current_user)
    return {
        "message": "Successfully logged out",
    }
