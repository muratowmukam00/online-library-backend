from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_all_categories(db: Session) -> List[Category]:
    """Retrieves all categories from the database."""
    return db.query(Category).all()


def get_category_by_id(db: Session, category_id: int) -> Category:
    """Retrieves a category by its id."""
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """Creates a new category."""
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
    """Update an existing category."""
    category_to_update = get_category_by_id(db, category_id)
    if not category_to_update:
        return None

    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category_to_update, field, value)

    db.add(category_to_update)
    db.commit()
    db.refresh(category_to_update)
    return category_to_update


def delete_category_by_id(db: Session, category_id: int) -> bool:
    """Deletes a category by its id."""
    category_to_delete = get_category_by_id(db, category_id)
    if category_to_delete:
        db.delete(category_to_delete)
        db.commit()
        return True
    return False