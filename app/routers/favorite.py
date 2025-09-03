from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.schemas.user import UserResponse
from app.services import favorite_service

router = APIRouter(
    tags=["favorites"],
    dependencies=[Depends(get_current_user)],
)


@router.post('/', response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
        favorite_data: FavoriteCreate,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user),
):
    book = favorite_service.get_book_by_id(db, favorite_data.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    existing_favorite = favorite_service.get_favorite_by_book_and_user(
        db, book_id=favorite_data.book_id, user_id=current_user.id
    )
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book is already in favorite",
        )

    new_favorite = favorite_service.create_favorite(db, favorite_data, current_user.id)
    return new_favorite


@router.get('/', response_model=List[FavoriteResponse], status_code=status.HTTP_200_OK)
def get_favorites(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    favorites = favorite_service.get_favorites_for_user(db, current_user.id)
    return favorites


@router.delete('/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
        book_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user),
):
    favorite_item = favorite_service.get_favorite_by_book_and_user(db, book_id, current_user.id)
    if not favorite_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite book not found")

    favorite_service.delete_favorite_item(db, favorite_item)
    return