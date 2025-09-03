from pydantic import BaseModel
from typing import List, Optional

from app.schemas.book import BookResponse

class ReadingListBase(BaseModel):
    title: str

class ReadingListCreate(ReadingListBase):
    pass

class ReadingListBookAdd(BaseModel):
    book_id: int

class ReadingListResponse(ReadingListBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class ReadingListWithBooksResponse(ReadingListResponse):
    books: List[BookResponse] = []