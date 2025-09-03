from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("rating", "book_id", name="unique_review_per_user_book"),
    )

    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")