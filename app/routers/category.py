from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

public_router = APIRouter(
    prefix="/category",
    tags=["category (public)"],
)

admin_router = APIRouter(
    prefix="/category",
    tags=["category (admin)"],
    dependencies=[Depends(get_current_admin)],
)


@public_router.get("/", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def get_all_categories(db: Session = Depends(get_db)):
    all_categories = db.query(Category).all()
    return all_categories


@public_router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@admin_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(*, db: Session = Depends(get_db), category_data: CategoryCreate):
    new_category = Category(**category_data.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@admin_router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_data: CategoryUpdate,
):
    category_to_update = db.query(Category).filter(Category.id == category_id).first()
    if not category_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category_to_update, field, value)

    db.add(category_to_update)
    db.commit()
    db.refresh(category_to_update)
    return category_to_update

@admin_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(*, db: Session = Depends(get_db), category_id: int):
    category_to_delete = db.query(Category).filter(Category.id == category_id).first()
    if not category_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category_to_delete)
    db.commit()

    return



