from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.models.user import User
from app.services import review_service


router = APIRouter(
    tags=["reviews"],
)


@router.post("/books/{book_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review_for_book(
    book_id: int,
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review for a specific book."""
    book = review_service.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    new_review = review_service.create_review(db, book_id, current_user.id, review)
    return new_review


@router.get("/books/{book_id}", response_model=List[ReviewResponse])
def get_review_for_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all reviews for a specific book."""
    reviews = review_service.get_reviews_for_book(db, book_id)
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No reviews found for this book_id {book_id}")

    return reviews

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing review. Only the owner can update."""
    db_review = review_service.get_review_by_id(db, review_id)
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if current_user.id != db_review.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of the review")

    updated_review = review_service.update_review(db, review_id, review_data)
    return updated_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review. Only the owner or an admin can delete."""
    db_review = review_service.get_review_by_id(db, review_id)
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if current_user.id != db_review.user_id:
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this review.")

    success = review_service.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return