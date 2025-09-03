import shutil
import os
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from fastapi import UploadFile, HTTPException, status

from app.models.book import Book
from app.schemas.pagination import PaginationResponse


def get_all_books(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        sort_by: str = 'id',
        sort_order: str = 'asc',
        skip: int = 0,
        limit: int = 10,
) -> PaginationResponse:
    """Retrieve all books with filtering, sorting, and pagination."""

    query = db.query(Book)

    if search:
        query = query.filter(
            (Book.title.ilike(f"%{search}%")) | (Book.description.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if author_id:
        query = query.filter(Book.author_id == author_id)

    sortable_fields = ['id', 'title', 'author_id']
    if sort_by in sortable_fields:
        if sort_order.lower() == 'desc':
            query = query.order_by(desc(getattr(Book, sort_by)))
        else:
            query = query.order_by(asc(getattr(Book, sort_by)))

    total_book = query.count()

    all_books = query.offset(skip).limit(limit).all()

    return PaginationResponse(
        total=total_book,
        skip=skip,
        limit=limit,
        data=all_books,
    )


def get_book_by_id(db: Session, book_id: int,) -> Optional[Book]:
    """
    Retrieve a book by its ID.
    Includes related reviews to avoid N+1 query problem
    """
    return db.query(Book).options(joinedload(Book.reviews)).filter(Book.id == book_id).first()


def save_file(file: UploadFile, filename: str) -> Optional[str]:
    """Saves an uploaded file to the 'files' directory."""

    if not os.path.exists('files'):
        os.makedirs('files')

    file_path = os.path.join('files', filename)

    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        return filename
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


def create_book(
        db: Session,
        title: str,
        description: Optional[str],
        author_id: int,
        category_id: int,
        file: UploadFile,
) -> Book:
    """Creates a new book & save it associated file"""

    if db.query(Book).filter(Book.title == title).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with title '{title}' already exists.",
        )

    file_extension = file.filename.split('.')[-1].lower() if file.filename else ""
    if file_extension != 'pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    unique_filename = f"{title.replace(' ', '_')}_{author_id}.{file_extension}"
    file_path = save_file(file, unique_filename)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file",
        )
    new_book = Book(
        title=title,
        description=description,
        author_id=author_id,
        category_id=category_id,
        file_path=file_path,
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


def update_book(
        db: Session,
        book_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        file: Optional[UploadFile] = None,
) ->Optional[Book]:
    """Updates an existing book & save its associated file"""

    book = get_book_by_id(db, book_id)
    if not book:
        return None

    old_file_path = book.file_path
    old_title = book.title

    if title and title != old_title:
        if db.query(Book).filter(Book.title == title).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with title '{title}' already exists.",
            )
        book.title = title

    if description is not None:
        book.description = description
    if author_id is not None:
        book.author_id = author_id
    if category_id is not None:
        book.category_id = category_id

    if file:
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ""
        if file_ext != 'pdf':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        if os.path.exists(old_file_path):
            os.remove(old_file_path)

        unique_filename = f"{title.replace(' ', '_')}_{author_id}.{file_ext}"
        file_path = save_file(file, unique_filename)
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file",
            )
        book.file_path = file_path

    elif title and title != old_title:
        file_ext = os.path.splitext(old_file_path)[1]
        unique_filename = f"{title.replace(' ', '_')}_{author_id}{file_ext}"
        new_file_path = os.path.join('files', unique_filename)

        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            book.file_path = new_file_path
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> bool:
    """Deletes an existing book & its associated file"""

    book_to_delete = get_book_by_id(db, book_id)
    if not book_to_delete:
        return False

    if os.path.exists(book_to_delete.file_path):
        os.remove(book_to_delete.file_path)

    db.delete(book_to_delete)
    db.commit()
    return True