from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin

from app.schemas.author import AuthorCreate, AuthorResponse, AuthorUpdate
from app.services import author_service

public_router = APIRouter(
    tags=["author (public)"],
)

admin_router = APIRouter(
    tags=["author (admin)"],
    dependencies=[Depends(get_current_admin)],
)



@public_router.get("/", response_model=List[AuthorResponse])
def get_authors(db: Session = Depends(get_db)):
    """Return all authors."""

    all_authors = author_service.get_all_authors(db)
    return all_authors


@public_router.get("/{author_id}", response_model=AuthorResponse)
def get_author_by_id(*, db: Session = Depends(get_db), author_id: int):
    """Return author by their id."""

    author = author_service.get_author_by_id(db, author_id)

    if not author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    return author


@admin_router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(author_data: AuthorCreate, db: Session = Depends(get_db)):
    """Create a new author."""

    new_author = author_service.create_author(db, author_data)
    return new_author


@admin_router.put("/{author_id}", response_model=AuthorResponse)
def update_author(author_id: int, author_data: AuthorUpdate, db: Session = Depends(get_db)):
    """Update an existing author. (Admin only)."""

    author_to_update = author_service.update_author(db, author_id, author_data)

    if not author_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

    return author_to_update


@admin_router.delete("/{author_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, db: Session = Depends(get_db),):
    """Delete an existing author. (Admin only)."""

    if not author_service.delete_author(db, author_id):
        raise HTTPException(status_code=404, detail="Author not found")
    return