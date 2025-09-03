from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .user import UserResponse
from .book import BookResponse


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="The rating of the review [1, 5].")
    comment: Optional[str] = Field(None, description="The comment of the review.")


class ReviewUpdate(BaseModel):
    rating: int = Field(None, ge=1, le=5, description="The rating of the review.")
    comment: Optional[str] = Field(None, max_length=1000, description="The comment of the review.")


class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user: UserResponse
    book: BookResponse

    class Config:
        from_attributes = True
