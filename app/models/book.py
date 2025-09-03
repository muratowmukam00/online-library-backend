from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.reading_list import reading_list_books


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    reviews = relationship("Review", back_populates="book")
    favorites = relationship("Favorite", back_populates="book")
    reading_lists = relationship("ReadingList",reading_list_books,back_populates="books")

