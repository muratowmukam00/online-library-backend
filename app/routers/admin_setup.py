from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.admin_setup_service import create_first_admin_user

router = APIRouter(
    tags=["create-first-admin"],
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_initial_admin_endpoint(
        user_data: UserCreate,
        db: Session = Depends(get_db),
):
    """
    Endpoint for initial settings system.
    Create firs & alone admin user if it doesn't exist.
    """
    if db.query(User).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already exists. This endpoint is for initial setup only."
        )

    new_admin_user = create_first_admin_user(db, user_data)
    return new_admin_user