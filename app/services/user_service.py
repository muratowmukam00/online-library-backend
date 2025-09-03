from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import get_password_hash


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retrieve a list of all users from the database."""

    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by their ID."""

    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by their username."""

    return db.query(User).filter(User.username == username).first()


def update_user_profile(db: Session, user: User, user_data: UserUpdate) -> User:
    """
    Update a user's profile with the given data.
    Handles uniqueness checks for username and email, and password hashing.
    """

    update_data = user_data.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] != user.username:
        existing_user = db.query(User).filter(User.username == update_data["username"]).first()
        if existing_user:
            return None

    if "email" in update_data and update_data["email"] != user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user:
            return None

    for key, value in update_data.items():
        if key == "password":
            setattr(user, 'hashed_password', get_password_hash(value))
        else:
            setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> bool:
    """Delete a user by their ID."""

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False