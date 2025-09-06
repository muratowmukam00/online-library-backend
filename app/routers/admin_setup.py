from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter(
    prefix="/create-first-admin",
    tags=["create-first-admin"],
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_first_admin_user(*, db: Session = Depends(get_db), user_data: UserCreate):
    if db.query(User).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already exists. This endpoint is for initial setup only.",
        )
    hashed_password: str = get_password_hash(user_data.password)
    new_admin_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=True
    )
    db.add(new_admin_user)
    db.commit()
    db.refresh(new_admin_user)
    return new_admin_user