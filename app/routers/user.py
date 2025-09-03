from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.database import get_db
from app.core.security import get_current_admin, get_user_with_relations
from app.services import user_service

router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_user_with_relations)):
    """Get the profile of the currently authenticated user."""

    return current_user


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_with_relations)
):
    """Update the authenticated user's profile."""

    updated_user = user_service.update_user_profile(db=db, user=current_user, user_data=user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already in use."
        )

    return updated_user


@router.get('/', response_model=List[UserResponse])
def get_all_users(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Retrieve a list of all users (admin only)."""

    users = user_service.get_all_users(db=db, skip=skip, limit=limit)
    return users


@router.get('/{user_id}', response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get a user by their ID (admin only)."""

    user = user_service.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.patch('/{user_id}', response_model=UserResponse)
def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update a user's profile by their ID (admin only)."""

    user_to_update = user_service.get_user_by_id(db=db, user_id=user_id)
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = user_service.update_user_profile(db=db, user=user_to_update, user_data=user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already in use."
        )

    return updated_user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a user by their ID (admin only)."""

    if not user_service.delete_user_by_id(db=db, user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return