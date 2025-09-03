from pydantic import BaseModel
from typing import Optional, List

from app.schemas.author import AuthorResponse
from app.schemas.category import CategoryResponse


class BookBase(BaseModel):
    title: str
    description: str


class BookCreate(BookBase):
    author_id: int
    category_id: int

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None


class BookResponse(BookBase):
    id: int
    file_path: str

    author: AuthorResponse
    category: CategoryResponse

    class Config:
        from_attributes = True


class BookPaginationResponse(BaseModel):
    total: int
    skip: int
    limit: int
    data: List[BookResponse]
