from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def create_first_admin_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new admin user
    Checks if the user is already have admin account & hashed password
    """
    hashed_password: str = get_password_hash(user_data.password)
    new_admin = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=True
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin