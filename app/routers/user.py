from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import decode_access_token
from app.routers.auth import get_db

router = APIRouter()

@router.get("/me")
def read_user_me(username: str = Depends(decode_access_token), db: Session = Depends(get_db)):
    # noinspection PyTypeChecker
    user = db.query(User).filter(User.username == username).first()
    return user