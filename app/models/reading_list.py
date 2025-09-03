from sqlalchemy import Column, ForeignKey, Integer, String, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


reading_list_books = Table(
    "reading_list_books",Base.metadata,
    Column("reading_list_id", Integer,
           ForeignKey("reading_lists.id", ondelete="CASCADE"), primary_key=True),
    Column("book_id", Integer,
           ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
)


class ReadingList(Base):
    __tablename__ = 'reading_lists'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    user = relationship("User", back_populates="reading_lists")
    books = relationship(
        "Book",
        secondary=reading_list_books,
        back_populates="reading_lists"
    )