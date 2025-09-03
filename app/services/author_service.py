from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate

def get_all_authors(db: Session) -> List[Author]:
    """Retrieve all authors from the database."""
    return db.query(Author).all()


def get_author_by_id(db: Session, author_id: int) -> Optional[Author]:
    """Retrieve author by id from the database."""
    return db.query(Author).filter(Author.id == author_id).first()


def create_author(db: Session, author_data: AuthorCreate) -> Author:
    """Create a new author."""

    new_author = Author(**author_data.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

def update_author(db: Session, author_id: int, author_data: AuthorUpdate) -> Optional[Author]:
    """Update author by id from the database."""

    author_to_update = get_author_by_id(db, author_id)
    if not author_to_update:
        return None

    for field, value in author_data.model_dump().items():
        setattr(author_to_update, field, value)

    db.add(author_to_update)
    db.commit()
    db.refresh(author_to_update)
    return author_to_update


def delete_author(db: Session, author_id: int) -> bool:
    """Delete author by id from the database."""

    author_to_delete = get_author_by_id(db, author_id)
    if author_to_delete:
        db.delete(author_to_delete)
        db.commit()
        return True
    return False
