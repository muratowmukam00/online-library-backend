from pydantic import BaseModel

from .book import BookResponse

class FavoriteBase(BaseModel):
    book_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    book: BookResponse

    class Config:
        from_attributes = True
