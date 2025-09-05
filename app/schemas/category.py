from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class AuthorCreate(CategoryBase):
    pass

class AuthorUpdate(CategoryBase):
    pass

class AuthorResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True