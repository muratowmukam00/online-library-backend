from fastapi.testclient import TestClient




def test_get_all_categories_empty(client: TestClient):
    response = client.get("/public/categories/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_categories_after_creation(admin_client: TestClient):
    payload = {"name": "Science"}
    create_res = admin_client.post("/admin/categories/", json=payload)
    assert create_res.status_code == 201

    response = admin_client.get("/public/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Science"


def test_get_category_by_id(client: TestClient, admin_client: TestClient):
    payload = {"name": "History"}
    create_res = admin_client.post("/admin/categories/", json=payload)
    cat_id = create_res.json()["id"]

    response = client.get(f"/public/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "History"


def test_get_category_by_id_not_found(client: TestClient):
    response = client.get("/public/categories/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"



def test_create_category_as_admin(admin_client: TestClient):
    payload = {"name": "Philosophy"}
    response = admin_client.post("/admin/categories/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Philosophy"
    assert "id" in data


def test_create_category_as_non_admin(authenticated_client: TestClient):
    payload = {"name": "Biology"}
    response = authenticated_client.post("/admin/categories/", json=payload)
    assert response.status_code in (401, 403)  # depending on your security logic


def test_update_category(admin_client: TestClient):
    create_res = admin_client.post("/admin/categories/", json={"name": "OldName"})
    cat_id = create_res.json()["id"]

    response = admin_client.put(f"/admin/categories/{cat_id}", json={"name": "NewName"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cat_id
    assert data["name"] == "NewName"


def test_update_category_not_found(admin_client: TestClient):
    response = admin_client.put("/admin/categories/9999", json={"name": "DoesNotExist"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_category(admin_client: TestClient):
    create_res = admin_client.post("/admin/categories/", json={"name": "ToDelete"})
    cat_id = create_res.json()["id"]

    response = admin_client.delete(f"/admin/categories/{cat_id}")
    assert response.status_code == 204

    get_res = admin_client.get(f"/public/categories/{cat_id}")
    assert get_res.status_code == 404


def test_delete_category_not_found(admin_client: TestClient):
    response = admin_client.delete("/admin/categories/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"