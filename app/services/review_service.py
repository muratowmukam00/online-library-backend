from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.book import Book
from app.schemas.review import ReviewCreate, ReviewUpdate


def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
    """Retrieve a book by its ID."""
    return db.query(Book).filter(Book.id == book_id).first()


def get_review_by_id(db: Session, review_id: int) -> Optional[Review]:
    """Retrieve a review by its ID."""
    return db.query(Review).filter(Review.id == review_id).first()


def get_reviews_for_book(db: Session, book_id: int) -> List[Review]:
    """Retrieve all reviews for a specific book."""
    return db.query(Review).filter(Review.book_id == book_id).all()


def create_review(db: Session, book_id: int, user_id: int, review_data: ReviewCreate) -> Review:
    """Create a new review for a book."""
    db_review = Review(
        **review_data.model_dump(),
        book_id=book_id,
        user_id=user_id,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
    """Update an existing review by its ID."""
    db_review = get_review_by_id(db, review_id)
    if not db_review:
        return None

    for key, value in review_data.model_dump(exclude_unset=True).items():
        setattr(db_review, key, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    """Delete a review by its ID."""
    db_review = get_review_by_id(db, review_id)
    if not db_review:
        return False

    db.delete(db_review)
    db.commit()
    return True