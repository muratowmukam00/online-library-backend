import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User

TEST_USER_DATA = {
    "username": "testuser",
    "password": "TestPassword123!",
    "email": "testuser@example.com"
}

ADMIN_USER_DATA = {
    "username": "adminuser",
    "password": "AdminPassword123!",
    "email": "admin@example.com"
}

EXTRA_USER_DATA = {
    "username": "extrauser",
    "password": "ExtraPassword123!",
    "email": "extra@example.com"
}


@pytest.fixture
def authenticated_client(client: TestClient):
    client.post("/auth/register", json=TEST_USER_DATA)

    login_data = {"username": TEST_USER_DATA["username"], "password": TEST_USER_DATA["password"]}
    response = client.post("/auth/login", data=login_data)
    access_token = response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    client.headers.pop("Authorization", None)


@pytest.fixture
def admin_client(client: TestClient, db_session: Session):

    client.post("/auth/register", json=ADMIN_USER_DATA)

    admin_user = db_session.query(User).filter(User.email == ADMIN_USER_DATA["email"]).first()
    admin_user.is_admin = True
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    login_data = {"username": ADMIN_USER_DATA["username"], "password": ADMIN_USER_DATA["password"]}
    response = client.post("/auth/login", data=login_data)
    access_token = response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    client.headers.pop("Authorization", None)



def test_get_my_profile_successfully(authenticated_client: TestClient):
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == TEST_USER_DATA["username"]
    assert data["email"] == TEST_USER_DATA["email"]


def test_get_my_profile_unauthorized(client: TestClient):

    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_my_profile_successfully(authenticated_client: TestClient):

    update_data = {"email": "new_test_email@example.com"}
    response = authenticated_client.patch("/users/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == update_data["email"]


def test_update_my_profile_with_existing_email_fails(authenticated_client: TestClient, client: TestClient):

    client.post("/auth/register", json=EXTRA_USER_DATA)
    update_data = {"email": EXTRA_USER_DATA["email"]}
    response = authenticated_client.patch("/users/me", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email is already in use."



def test_get_all_users_as_admin_successfully(admin_client: TestClient):
    admin_client.post("/auth/register", json=TEST_USER_DATA)
    response = admin_client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_all_users_as_normal_user_fails(authenticated_client: TestClient):
    response = authenticated_client.get("/users/")
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this resource"


def test_get_user_by_id_as_admin_successfully(admin_client: TestClient):
    unique_user_data = {
        "username": "unique_user_1",
        "password": "Password123!",
        "email": "unique_user_1@example.com"
    }
    response = admin_client.post("/auth/register", json=unique_user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    response = admin_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_get_nonexistent_user_as_admin_fails(admin_client: TestClient):
    non_existent_id = 9999
    response = admin_client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_by_id_as_admin_successfully(admin_client: TestClient):
    unique_user_data = {
        "username": "unique_user_2",
        "password": "Password123!",
        "email": "unique_user_2@example.com"
    }
    response = admin_client.post("/auth/register", json=unique_user_data)
    assert response.status_code == 201
    user_id = response.json()["id"]

    delete_response = admin_client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204

    get_response = admin_client.get(f"/users/{user_id}")
    assert get_response.status_code == 404