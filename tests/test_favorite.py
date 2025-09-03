import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.models.favorite import Favorite
from app.services import book_service



@pytest.fixture(scope="function")
def create_test_book(db_session: Session):
    """
    Creates an author, a category, and a book for testing purposes.
    Returns the created book object.
    """
    author = Author(name="Test Author")
    category = Category(name="Test Category")
    db_session.add(author)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(author)
    db_session.refresh(category)

    from fastapi import UploadFile
    from io import BytesIO
    test_pdf_content = b"This is a test PDF file for a favorite book."
    test_file = UploadFile(filename="favorite_test_book.pdf", file=BytesIO(test_pdf_content))

    book = book_service.create_book(
        db_session,
        title="Favorite Test Book",
        description="A book for favorite tests.",
        author_id=author.id,
        category_id=category.id,
        file=test_file,
    )
    return book



def test_add_favorite_success(authenticated_client: TestClient, create_test_book: Book, db_session: Session):
    book_id = create_test_book.id
    response = authenticated_client.post(
        "/favorites/",
        json={"book_id": book_id}
    )
    assert response.status_code == 201
    assert response.json()["book_id"] == book_id
    assert "id" in response.json()

    # Verify that the favorite record exists in the database
    favorite_item = db_session.query(Favorite).filter_by(book_id=book_id).first()
    assert favorite_item is not None
    assert favorite_item.book_id == book_id


def test_add_favorite_book_not_found(authenticated_client: TestClient):
    response = authenticated_client.post(
        "/favorites/",
        json={"book_id": 99999}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_add_favorite_duplicate(authenticated_client: TestClient, create_test_book: Book):
    book_id = create_test_book.id
    # First request adds the book
    authenticated_client.post("/favorites/", json={"book_id": book_id})

    # Second request should fail with a 409 conflict
    response = authenticated_client.post(
        "/favorites/",
        json={"book_id": book_id}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Book is already in favorite"


def test_get_favorites_empty(authenticated_client: TestClient):
    response = authenticated_client.get("/favorites/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_favorites(authenticated_client: TestClient, create_test_book: Book):
    book_id = create_test_book.id
    authenticated_client.post("/favorites/", json={"book_id": book_id})

    response = authenticated_client.get("/favorites/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["book_id"] == book_id
    assert response.json()[0]["book"]["title"] == "Favorite Test Book"


def test_delete_favorite_success(authenticated_client: TestClient, create_test_book: Book, db_session: Session):
    book_id = create_test_book.id
    authenticated_client.post("/favorites/", json={"book_id": book_id})

    response = authenticated_client.delete(f"/favorites/{book_id}")
    assert response.status_code == 204

    favorite_item = db_session.query(Favorite).filter_by(book_id=book_id).first()
    assert favorite_item is None


def test_delete_favorite_not_found(authenticated_client: TestClient):
    response = authenticated_client.delete("/favorites/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Favorite book not found"