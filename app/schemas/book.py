from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    author_id: int
    category_id: int

class BookCreate(BookBase):
    pass

class BookResponse(BaseModel):
    id: int
    file_path: Optional[str] = None
    title: str
    description: Optional[str] = None
    author_id: int
    category_id: int

    class Config:
        from_attributes = True

class BookUpdate(BookBase):


    class Config:
        from_attributes = True