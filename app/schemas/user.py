from pydantic import BaseModel, EmailStr, validator, field_validator
from typing import Optional, List

from app.schemas.reading_list import ReadingListWithBooksResponse

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


    @field_validator('password')
    @classmethod
    def validate_password_length(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    reading_lists: List[ReadingListWithBooksResponse]

    class Config:
        from_attributes = True
