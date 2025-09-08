import shutil
import os
from http.client import HTTPResponse
from typing import Optional, List

from fastapi import APIRouter,Depends, status, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin

from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse


admin_router = APIRouter(
    prefix="/book",
    tags=["book (admin)"],
    dependencies=[Depends(get_current_admin)],
)


public_router = APIRouter(
    prefix="/book",
    tags=["book (public)"],
)


@public_router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
def get_all_books(db: Session = Depends(get_db)):
    all_books = db.query(Book).all()
    return all_books


@public_router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book(*, db: Session = Depends(get_db), book_id: int):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@admin_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
        *,
        db: Session = Depends(get_db),
        title: str = Form(...),
        description: Optional[str] = Form(None),
        author_id: int = Form(...),
        category_id: int = Form(...),
        file: UploadFile = File(...),
):
    try:
        # Ваш существующий код
        existing_book = db.query(Book).filter(Book.title == title).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book already exists",
            )

        file_extension = file.filename.split(".")[-1] if file.filename else ""
        if file_extension.lower() != 'pdf':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed",
            )

        if not os.path.exists('files'):
            os.makedirs('files')
        unique_filename = f"{title.replace(" ", "_")}_{author_id}.{file_extension}"
        file_path = os.path.join('files', unique_filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

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

    except HTTPException as e:
        # Перехватываем HTTPException и повторно выбрасываем её.
        # Таким образом, FastAPI обработает её без проблем.
        raise e

    except Exception as e:
        # Обрабатываем любые другие неожиданные ошибки и
        # возвращаем простой, "безопасный" HTTPException.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {str(e)}"
        )

@admin_router.put("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def update_book(
        *,
        db: Session = Depends(get_db),
        book_id: int,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        author_id: Optional[int] = Form(None),
        category_id: Optional[int] = Form(None),
        file: UploadFile = File(None),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if title and title != book.title:
        existing_book = db.query(Book).filter(Book.title == title).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book with this title already exists",
            )
        book.title = title

    if description is not None:
        book.description = description
    if author_id is not None:
        book.author_id = author_id
    if category_id is not None:
        book.category_id = category_id

    if file:
        file_extension = file.filename.split(".")[-1] if file.filename else ""
        if file_extension != "pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed",
            )

        if os.path.exists(book.file_path):
            os.remove(book.file_path)

        unique_filename = f"{book.title.replace(' ', '_')}_{book.author_id}.{file_extension}"
        file_path = os.path.join('files', unique_filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        book.file_path = file_path

    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@admin_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(*, db: Session = Depends(get_db), book_id: int):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()



