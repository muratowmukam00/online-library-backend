from pydantic import BaseModel
from typing import List, Generic, TypeVar, Optional

T = TypeVar("T")

class PaginationResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    data: List[T]
