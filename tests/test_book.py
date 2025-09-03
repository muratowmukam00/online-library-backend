import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.services import book_service as book_service


@pytest.fixture(scope="function", autouse=True)
def setup_data(db_session: Session):
    author = Author(name="Test Author")
    category = Category(name="Test Category")
    db_session.add(author)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(author)
    db_session.refresh(category)
    return author, category


@pytest.fixture(scope="function")
def create_test_book(db_session: Session, setup_data):
    author, category = setup_data

    from fastapi import UploadFile
    from io import BytesIO
    test_pdf_content = b"This is a test PDF file."
    test_file = UploadFile(filename="test_book.pdf", file=BytesIO(test_pdf_content))

    book = book_service.create_book(
        db_session,
        title="Test Book Title",
        description="Test book description.",
        author_id=author.id,
        category_id=category.id,
        file=test_file,
    )
    return book


def test_get_public_books_empty(client: TestClient):
    response = client.get("/public/books/")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["data"] == []


def test_get_public_books(client: TestClient, create_test_book):
    response = client.get("/public/books/")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["data"][0]["title"] == "Test Book Title"


def test_get_public_book_by_id(client: TestClient, create_test_book):
    book_id = create_test_book.id
    response = client.get(f"/public/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book Title"
    assert response.json()["author"]["name"] == "Test Author"


def test_get_public_book_not_found(client: TestClient):
    response = client.get("/public/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"



def test_create_book_admin_success(admin_client: TestClient, setup_data):
    author, category = setup_data

    with open("tests/temp_test_file.pdf", "wb") as f:
        f.write(b"Test content for a new book.")

    with open("tests/temp_test_file.pdf", "rb") as f:
        response = admin_client.post(
            "/admin/books/",
            data={
                "title": "New Book",
                "description": "A new book created via API.",
                "author_id": author.id,
                "category_id": category.id,
            },
            files={"file": ("new_book.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201
    assert response.json()["title"] == "New Book"
    assert "id" in response.json()

    os.remove("tests/temp_test_file.pdf")


def test_create_book_admin_duplicate_title(admin_client: TestClient, create_test_book, setup_data):
    author, category = setup_data

    with open("tests/temp_test_file.pdf", "wb") as f:
        f.write(b"Test content for a duplicate book.")

    with open("tests/temp_test_file.pdf", "rb") as f:
        response = admin_client.post(
            "/admin/books/",
            data={
                "title": "Test Book Title",
                "description": "Duplicate test.",
                "author_id": author.id,
                "category_id": category.id,
            },
            files={"file": ("duplicate_book.pdf", f, "application/pdf")},
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Book with title 'Test Book Title' already exists."

    os.remove("tests/temp_test_file.pdf")


def test_update_book_admin(admin_client: TestClient, create_test_book, db_session: Session):
    book_id = create_test_book.id
    response = admin_client.put(
        f"/admin/books/{book_id}",
        data={"title": "Updated Book Title"}
    )


def test_delete_book_admin(admin_client: TestClient, create_test_book, db_session: Session):
    book_id = create_test_book.id
    response = admin_client.delete(f"/admin/books/{book_id}")
    assert response.status_code == 204

    deleted_book = db_session.query(Book).get(book_id)
    assert deleted_book is None

    os.path.exists(create_test_book.file_path)


def test_delete_book_not_found(admin_client: TestClient):
    response = admin_client.delete("/admin/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"