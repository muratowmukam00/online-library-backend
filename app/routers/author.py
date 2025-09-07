from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin

from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorResponse, AuthorUpdate

public_router = APIRouter(
    prefix="/author",
    tags=["author (public)"],
)

admin_router = APIRouter(
    prefix="/author",
    tags=["author (admin)"],
    dependencies=[Depends(get_current_admin)],
)



@public_router.get("/", response_model=List[AuthorResponse])
def get_authors(*, db: Session = Depends(get_db)):
    all_authors = db.query(Author).all()
    return all_authors


@public_router.get("/{author_id}", response_model=AuthorResponse)
def get_author_by_id(*, db: Session = Depends(get_db), author_id: int):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@admin_router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(*, db: Session = Depends(get_db), author_data: AuthorCreate):
    new_author = Author(**author_data.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author


@admin_router.put("/{author_id}", response_model=AuthorResponse)
def update_author(*, db: Session = Depends(get_db), author_id: int, author_data: AuthorUpdate):
    author_to_update = db.query(Author).filter(Author.id == author_id).first()
    if not author_to_update:
        raise HTTPException(status_code=404, detail="Author not found")

    for field, value in author_data.model_dump(exclude_unset=True).items():
        setattr(author_to_update, field, value)
    db.add(author_to_update)
    db.commit()
    db.refresh(author_to_update)
    return author_to_update

@admin_router.delete("/{author_id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_author(*, db: Session = Depends(get_db), author_id: int):
    author_to_delete = db.query(Author).filter(Author.id == author_id).first()
    if not author_to_delete:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author_to_delete)
    db.commit()
    return