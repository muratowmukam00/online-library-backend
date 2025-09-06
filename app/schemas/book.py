from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    author_id: int
    category_id: int

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    id: int
    file_path: Optional[str] = None

    class Config:
        from_attributes = True