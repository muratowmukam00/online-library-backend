from typing import Optional
from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = None


class AuthorResponse(AuthorBase):
    id: int

    class Config:
        from_attributes = True
