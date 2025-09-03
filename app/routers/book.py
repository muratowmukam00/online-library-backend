import shutil
import os
from typing import Optional, List

from fastapi import APIRouter,Depends, status, HTTPException, File, UploadFile, Form
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_admin

from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookPaginationResponse
from app.schemas.pagination import PaginationResponse
from app.services import book_service


admin_router = APIRouter(
    tags=["book (admin)"],
    dependencies=[Depends(get_current_admin)],
)

public_router = APIRouter(
    tags=["book (public)"],
)


@public_router.get("/", response_model=PaginationResponse[BookResponse], status_code=status.HTTP_200_OK)
def get_all_books(
        db: Session = Depends(get_db),
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        sort_by: str = 'id',
        sort_order: str = 'asc',
        skip: int = 0,
        limit: int = 10,
):
    """Retrieve a paginated list of all books with optional search, filtering & sorting."""
    return book_service.get_all_books(
        db, search, category_id, author_id, sort_by, sort_order, skip, limit
    )


@public_router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Retrieve a single book by its ID"""

    book = book_service.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@admin_router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
        title: str = Form(...),
        description: Optional[str] = Form(None),
        author_id: int = Form(...),
        category_id: int = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    """Create a new book with an associated PDF file (admin only)."""
    try:
        return book_service.create_book(db, title, description, author_id, category_id, file)
    except HTTPException as err:
        raise err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interval an error occurred: {str(err)}",
        )


@admin_router.put("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book(
        book_id: int,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        author_id: Optional[int] = Form(None),
        category_id: Optional[int] = Form(None),
        file: UploadFile = File(None),
        db: Session = Depends(get_db),
):
    """Update an existing book by its ID."""
    updated_book = book_service.update_book(
        db=db,
        book_id=book_id,
        title=title,
        description=description,
        author_id=author_id,
        category_id=category_id,
        file=file,
    )
    if not updated_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated_book


@admin_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db),):
    if not book_service.delete_book(db, book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return




