from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.schemas.reading_list import ReadingListResponse, ReadingListCreate, ReadingListBookAdd, ReadingListWithBooksResponse
from app.services import reading_list_service


router = APIRouter(
    tags=["reading"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ReadingListResponse, status_code=status.HTTP_201_CREATED)
def create_reading_list(
        reading_list_data: ReadingListCreate,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """Create a new reading list for a current user."""
    new_list = reading_list_service.create_reading_list(db, reading_list_data.title, current_user.id)
    return new_list


@router.get("/", response_model=List[ReadingListResponse], status_code=status.HTTP_200_OK)
def get_all_reading_lists(
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve all reading lists belonging to the current user."""
    lists= reading_list_service.get_all_reading_lists(db, current_user.id)
    return lists


@router.get("/{list_id}", response_model=ReadingListWithBooksResponse, status_code=status.HTTP_200_OK)
def get_single_reading_list(
        list_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve a specific reading list by ID, including its books."""

    reading_list = reading_list_service.get_reading_list_by_id(db, list_id, current_user.id)
    if not reading_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ReadingList not found | you don't have permission")
    return reading_list


@router.post("/{list_id}/books", status_code=status.HTTP_204_NO_CONTENT)
def add_book_to_reading_list(
        list_id: int,
        book_data: ReadingListBookAdd,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """Add a book to a reading list."""
    reading_list = reading_list_service.get_reading_list_by_id(db, list_id, current_user.id)
    if not reading_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading list not found or you don't have permission"
        )

    success = reading_list_service.add_book_to_reading_list(db, reading_list, book_data.book_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Book already in the reading list or not found")
    return


@router.delete("/{list_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_from_reading_list(
        list_id: int,
        book_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(get_current_user)
):
    """Remove a book from a reading list."""
    reading_list = reading_list_service.get_reading_list_by_id(db, list_id, current_user.id)
    if not reading_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading list not found or you don't have permission"
        )

    success = reading_list_service.remove_book_from_reading_list(db, reading_list, book_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found in this reading list")
    return