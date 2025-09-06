from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin

from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorResponse

router = APIRouter(
    prefix="/author",
    tags=["author"],
    dependencies=[Depends(get_current_admin)],
)

@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
def create_author(*, db: Session = Depends(get_db), author_data: AuthorCreate):
    new_author = Author(**author_data.dict())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author