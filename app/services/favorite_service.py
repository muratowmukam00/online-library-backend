from typing import List
from sqlalchemy.orm import Session
from app.models.favorite import Favorite
from app.models.book import Book
from app.schemas.favorite import FavoriteCreate

def get_book_by_id(db: Session, book_id: int):
    """Get book with its ID."""
    return db.query(Book).filter_by(id=book_id).first()

def get_favorite_by_book_and_user(db: Session, book_id: int, user_id: int):
    return db.query(Favorite).filter_by(book_id=book_id, user_id=user_id).first()

def create_favorite(db: Session, favorite_data: FavoriteCreate, user_id: int):
    new_favorite = Favorite(user_id=user_id, book_id=favorite_data.book_id)
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    return new_favorite

def get_favorites_for_user(db: Session, user_id: int) -> List[Favorite]:
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()

def delete_favorite_item(db: Session, favorite_item: Favorite):
    db.delete(favorite_item)
    db.commit()