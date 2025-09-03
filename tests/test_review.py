import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.user import User
from app.models.review import Review
from app.models.author import Author
from app.models.category import Category
from app.services.user_service import get_user_by_username


@pytest.fixture
def create_test_book(db_session: Session) -> Book:
    """Fixture to create a test book and its dependencies."""
    test_author = db_session.query(Author).filter_by(name="Test Author").first()
    if not test_author:
        test_author = Author(name="Test Author")
        db_session.add(test_author)
        db_session.commit()
        db_session.refresh(test_author)

    test_category = db_session.query(Category).filter_by(name="Test Category").first()
    if not test_category:
        test_category = Category(name="Test Category")
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)

    book_data = {
        "title": "Test Book for Reviews",
        "description": "A book used for testing review functionality.",
        "author_id": test_author.id,
        "category_id": test_category.id,
        "file_path": "/path/to/test/file.pdf"  #
    }

    db_book = Book(**book_data)
    db_session.add(db_book)
    db_session.commit()
    db_session.refresh(db_book)
    return db_book


@pytest.fixture
def create_test_review(db_session: Session, create_test_book: Book, authenticated_client: TestClient) -> Review:
    """Fixture to create a test review."""
    user = get_user_by_username(db_session, "user")

    if not user:
        user = User(username="user", email="user@example.com", hashed_password="hashed_password")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    review_data = {
        "rating": 5,
        "comment": "This is a great book!",
        "book_id": create_test_book.id,
        "user_id": user.id
    }
    db_review = Review(**review_data)
    db_session.add(db_review)
    db_session.commit()
    db_session.refresh(db_review)
    return db_review


def test_create_review_success(authenticated_client: TestClient, db_session: Session, create_test_book: Book):
    """Test successful creation of a review."""
    review_data = {"rating": 4, "comment": "A very good read."}
    response = authenticated_client.post(f"/reviews/books/{create_test_book.id}", json=review_data)
    assert response.status_code == 201

    new_review = response.json()
    assert new_review["rating"] == 4
    assert new_review["comment"] == "A very good read."
    assert "id" in new_review

    # Verify review is in the database
    db_review = db_session.query(Review).get(new_review["id"])
    assert db_review is not None
    assert db_review.rating == 4


def test_create_review_book_not_found(authenticated_client: TestClient):
    """Test creating a review for a non-existent book."""
    review_data = {"rating": 3, "comment": "This book does not exist."}
    response = authenticated_client.post("/reviews/books/99999", json=review_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_create_review_unauthenticated(client: TestClient, create_test_book: Book):
    """Test creating a review without authentication."""
    review_data = {"rating": 2, "comment": "Unauthenticated test."}
    response = client.post(f"/reviews/books/{create_test_book.id}", json=review_data)
    assert response.status_code == 401


def test_get_reviews_for_book_success(client: TestClient, db_session: Session, create_test_review: Review):
    """Test retrieving all reviews for a specific book."""
    response = client.get(f"/reviews/books/{create_test_review.book_id}")
    assert response.status_code == 200

    reviews = response.json()
    assert isinstance(reviews, list)
    assert len(reviews) > 0
    assert reviews[0]["id"] == create_test_review.id
    assert reviews[0]["rating"] == create_test_review.rating


def test_get_reviews_for_book_not_found(client: TestClient):
    """Test retrieving reviews for a book that does not exist."""
    response = client.get("/reviews/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No reviews found for this book_id 99999"

# ---
def test_update_review_success(authenticated_client: TestClient, db_session: Session, create_test_review: Review):
    """Test successful update of a review by its owner."""
    review_update_data = {"comment": "An updated and better comment!"}
    response = authenticated_client.put(f"/reviews/{create_test_review.id}",
                                        json=review_update_data)  # Correct endpoint
    assert response.status_code == 200

    updated_review = response.json()
    assert updated_review["comment"] == "An updated and better comment!"

    db_review = db_session.query(Review).get(create_test_review.id)
    assert db_review.comment == "An updated and better comment!"


def test_update_review_forbidden(authenticated_client: TestClient, db_session: Session, create_test_review: Review):
    """Test that another user cannot update a review."""
    second_user = User(username="other_user", email="other@example.com", hashed_password="hashed_password",
                       is_admin=False, is_active=True)
    db_session.add(second_user)
    db_session.commit()
    db_session.refresh(second_user)

    another_review = Review(rating=3, comment="Another review", book_id=create_test_review.book_id,
                            user_id=second_user.id)
    db_session.add(another_review)
    db_session.commit()
    db_session.refresh(another_review)

    review_update_data = {"comment": "Trying to update someone else's review."}

    response = authenticated_client.put(f"/reviews/{another_review.id}", json=review_update_data)
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not the owner of the review"


def test_update_review_not_found(authenticated_client: TestClient):
    """Test updating a review that does not exist."""
    review_update_data = {"rating": 5}
    response = authenticated_client.put("/reviews/99999", json=review_update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"


# ---
def test_delete_review_success(authenticated_client: TestClient, db_session: Session, create_test_review: Review):
    """Test successful deletion of a review by its owner."""
    review_id = create_test_review.id
    response = authenticated_client.delete(f"/reviews/{review_id}")
    assert response.status_code == 204

    db_review = db_session.query(Review).get(review_id)
    assert db_review is None


def test_delete_review_admin_success(admin_client: TestClient, db_session: Session, create_test_review: Review):
    """Test successful deletion of a review by an admin."""
    review_id = create_test_review.id
    response = admin_client.delete(f"/reviews/{review_id}")
    assert response.status_code == 204


def test_delete_review_forbidden(authenticated_client: TestClient, db_session: Session, create_test_review: Review):
    """Test that another user cannot delete a review."""
    second_user = User(username="another_user", email="another@example.com", hashed_password="hashed_password",
                       is_admin=False, is_active=True)
    db_session.add(second_user)
    db_session.commit()
    db_session.refresh(second_user)

    another_review = Review(rating=2, comment="Another review to be deleted", book_id=create_test_review.book_id,
                            user_id=second_user.id)
    db_session.add(another_review)
    db_session.commit()
    db_session.refresh(another_review)

    response = authenticated_client.delete(f"/reviews/{another_review.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not authorized to delete this review."


def test_delete_review_not_found(authenticated_client: TestClient):
    """Test deleting a review that does not exist."""
    response = authenticated_client.delete("/reviews/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"