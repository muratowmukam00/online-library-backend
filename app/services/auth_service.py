from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    verify_password, get_password_hash, create_refresh_token,
    create_access_token, get_payload
)


def get_user_by_username_or_email(db: Session, username: str, email: str) -> Optional[User]:
    """"
    Get user by username or email
    """

    return db.query(User).filter(or_(User.username == username, User.email == email)).first()


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Register a new user.
    Hashes the password and saves the user to the database.
    """

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user: Optional[User] = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def create_user_tokens(db: Session, user: User) -> dict:
    """
    Create access and refresh tokens for a user.
    Stores the refresh token in the database.
    """
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_user_token(db: Session, refresh_token: str) -> str:
    """Refresh a user's access token using a valid refresh token."""
    payload = get_payload(refresh_token)
    username = payload.get("sub")
    token_type = payload.get("type")

    if username is None or token_type != "refresh":
        return None

    user = db.query(User).filter(User.username == username).first()
    if user and user.refresh_token == refresh_token:
        return create_access_token(data={"sub": username})

    return None


def logout_user(db: Session, current_user: User) -> None:
    """Logout a user."""

    current_user.refresh_token = None
    db.commit()