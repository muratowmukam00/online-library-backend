from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin

from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import category_service

public_router = APIRouter(
    tags=["category (public)"],
)

admin_router = APIRouter(
    tags=["category (admin)"],
    dependencies=[Depends(get_current_admin)],
)


@admin_router.get("/", status_code=status.HTTP_200_OK)
def test_admin_router():
    """Temporary route to check if admin_router is working."""
    return {"message": "Admin router is working!"}


@public_router.get("/", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def get_all_categories(db: Session = Depends(get_db)):
    """Retrieves all categories."""

    all_categories = category_service.get_all_categories(db)
    return all_categories


@public_router.get("/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Retrieve a category by its ID."""

    category = category_service.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@admin_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(*, db: Session = Depends(get_db), category_data: CategoryCreate):
    """Creates a new category. (Admins only!)"""

    new_category = category_service.create_category(db, category_data)
    return new_category


@admin_router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Updates a category. (Admins only!)"""

    category_to_update = category_service.update_category(db=db, category_id=category_id, category_data=category_data)
    if not category_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category_to_update


@admin_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Deletes a category by ID. (Admins only!)"""

    category_to_delete = category_service.delete_category_by_id(db, category_id)
    if not category_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return



