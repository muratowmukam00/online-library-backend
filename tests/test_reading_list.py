import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.services import book_service
from app.services import reading_list_service



@pytest.fixture(scope="function")
def create_test_book(db_session: Session):
    author = Author(name="Test Author for Reading List")
    category = Category(name="Test Category for Reading List")
    db_session.add(author)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(author)
    db_session.refresh(category)

    from fastapi import UploadFile
    from io import BytesIO
    test_pdf_content = b"This is a test PDF file."
    test_file = UploadFile(filename="test_book.pdf", file=BytesIO(test_pdf_content))

    book = book_service.create_book(
        db_session,
        title="Reading List Test Book",
        description="A book for testing reading lists.",
        author_id=author.id,
        category_id=category.id,
        file=test_file,
    )
    return book


@pytest.fixture(scope="function")
def create_reading_list(db_session: Session, authenticated_client: TestClient):
    response = authenticated_client.post(
        "/reading-lists/",
        json={"title": "My Test Reading List"}
    )
    assert response.status_code == 201
    return response.json()



def test_create_reading_list_success(authenticated_client: TestClient):
    response = authenticated_client.post(
        "/reading-lists/",
        json={"title": "A New Reading List"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "A New Reading List"
    assert "id" in response.json()


def test_get_all_reading_lists_empty(authenticated_client: TestClient):
    response = authenticated_client.get("/reading-lists/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_reading_lists(authenticated_client: TestClient, create_reading_list):
    response = authenticated_client.get("/reading-lists/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "My Test Reading List"


def test_get_single_reading_list_success(authenticated_client: TestClient, create_reading_list):
    list_id = create_reading_list["id"]
    response = authenticated_client.get(f"/reading-lists/{list_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "My Test Reading List"


def test_get_single_reading_list_not_found(authenticated_client: TestClient):
    response = authenticated_client.get("/reading-lists/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_add_book_to_reading_list_success(
        authenticated_client: TestClient,
        create_reading_list: dict,
        create_test_book: Book,
        db_session: Session
):
    list_id = create_reading_list["id"]
    book_id = create_test_book.id
    response = authenticated_client.post(
        f"/reading-lists/{list_id}/books",
        json={"book_id": book_id}
    )
    assert response.status_code == 204

    reading_list = reading_list_service.get_reading_list_by_id(db_session, list_id,1)
    assert len(reading_list.books) == 1
    assert reading_list.books[0].id == book_id


def test_add_book_to_reading_list_already_exists(
        authenticated_client: TestClient,
        create_reading_list: dict,
        create_test_book: Book
):
    list_id = create_reading_list["id"]
    book_id = create_test_book.id

    authenticated_client.post(
        f"/reading-lists/{list_id}/books",
        json={"book_id": book_id}
    )

    response = authenticated_client.post(
        f"/reading-lists/{list_id}/books",
        json={"book_id": book_id}
    )
    assert response.status_code == 409
    assert "already in the reading list" in response.json()["detail"]


def test_add_book_to_reading_list_not_found(
        authenticated_client: TestClient,
        create_reading_list: dict,
):
    list_id = create_reading_list["id"]
    response = authenticated_client.post(
        f"/reading-lists/{list_id}/books",
        json={"book_id": 99999}
    )
    assert response.status_code == 409
    assert "Book already in the reading list or not found" in response.json()["detail"]


def test_delete_book_from_reading_list_success(
        authenticated_client: TestClient,
        create_reading_list: dict,
        create_test_book: Book
):
    list_id = create_reading_list["id"]
    book_id = create_test_book.id

    authenticated_client.post(
        f"/reading-lists/{list_id}/books",
        json={"book_id": book_id}
    )

    response = authenticated_client.delete(
        f"/reading-lists/{list_id}/books/{book_id}"
    )
    assert response.status_code == 204

    response = authenticated_client.get(f"/reading-lists/{list_id}")
    assert response.json()["books"] == []


def test_delete_book_not_in_list(
        authenticated_client: TestClient,
        create_reading_list: dict
):
    list_id = create_reading_list["id"]
    response = authenticated_client.delete(
        f"/reading-lists/{list_id}/books/99999"
    )
    assert response.status_code == 404
    assert "not found in this reading list" in response.json()["detail"]


def test_delete_book_from_nonexistent_list(
        authenticated_client: TestClient,
        create_test_book: Book
):
    book_id = create_test_book.id
    response = authenticated_client.delete(
        f"/reading-lists/99999/books/{book_id}"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_reading_list_unauthorized(client: TestClient):
    response = client.get("/reading-lists/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"