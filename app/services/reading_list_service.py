from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.reading_list import ReadingList
from app.models.book import Book

def create_reading_list(db: Session, title: str, user_id: int,) -> ReadingList:
    """Create a new reading list for a user."""

    new_list = ReadingList(title=title, user_id=user_id)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


def get_all_reading_lists(db: Session, user_id: int) -> List[ReadingList]:
    """Get all reading lists for a specific user."""

    return db.query(ReadingList).filter(ReadingList.user_id == user_id).all()


def get_reading_list_by_id(db: Session, reading_list_id: int, user_id: int) -> Optional[ReadingList]:
    """
    Retrieve a specific reading list by its ID and user ownership.
    Includes associated books to prevent N+1 query problem.
    """
    return (
        db.query(ReadingList)
        .options(joinedload(ReadingList.books))
        .filter(ReadingList.id == reading_list_id, ReadingList.user_id == user_id)
        .first()
    )


def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
    """Retrieve a book by its ID."""
    return db.query(Book).filter(Book.id == book_id).first()


def add_book_to_reading_list(db: Session, reading_list: ReadingList, book_id: int) -> bool:
    """Add a book to the existing reading list."""

    book = get_book_by_id(db, book_id)
    if book is None:
        return False

    if book in reading_list.books:
        return False

    reading_list.books.append(book)
    db.commit()
    return True


def remove_book_from_reading_list(db: Session, reading_list: ReadingList, book_id: int) -> bool:
    """
    Remove a book from a reading list.
    This fixes the critical bug of deleting the entire book from the
    """

    book_to_delete = next((book for book in reading_list.books if book.id == book_id), None)
    if not book_to_delete:
        return False
    reading_list.books.remove(book_to_delete)
    db.commit()
    return True