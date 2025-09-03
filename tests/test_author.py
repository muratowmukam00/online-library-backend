import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.anyio


def test_get_authors_empty(client: TestClient):
    response = client.get("/public/authors/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_author(admin_client: TestClient):
    response = admin_client.post("/admin/authors/", json={"name": "Leo Tolstoy"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Leo Tolstoy"
    assert "id" in data


def test_get_authors(client: TestClient, admin_client: TestClient):
    admin_client.post("/admin/authors/", json={"name": "Fyodor Dostoevsky"})
    response = client.get("/public/authors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(author["name"] == "Fyodor Dostoevsky" for author in data)


def test_get_author_by_id(client: TestClient, admin_client: TestClient):
    create_res = admin_client.post("/admin/authors/", json={"name": "Anton Chekhov"})
    author_id = create_res.json()["id"]

    response = client.get(f"/public/authors/{author_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Anton Chekhov"


def test_get_author_by_id_not_found(client: TestClient):
    response = client.get("/public/authors/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


def test_update_author(admin_client: TestClient):
    create_res = admin_client.post("/admin/authors/", json={"name": "Old Name"})
    author_id = create_res.json()["id"]

    update_res = admin_client.put(f"/admin/authors/{author_id}", json={"name": "New Name"})
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "New Name"


def test_update_author_not_found(admin_client: TestClient):
    response = admin_client.put("/admin/authors/9999", json={"name": "Ghost"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


def test_delete_author(admin_client: TestClient):
    create_res = admin_client.post("/admin/authors/", json={"name": "ToDelete"})
    author_id = create_res.json()["id"]

    delete_res = admin_client.delete(f"/admin/authors/{author_id}")
    assert delete_res.status_code == 204

    get_res = admin_client.get(f"/authors/{author_id}")
    assert get_res.status_code == 404


def test_delete_author_not_found(admin_client: TestClient):
    response = admin_client.delete("/admin/authors/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"