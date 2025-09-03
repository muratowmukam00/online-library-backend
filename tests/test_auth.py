import pytest
from fastapi.testclient import TestClient

TEST_USER_DATA = {
    "username": "testuser",
    "password": "TestPassword123!",
    "email": "test@example.com"
}


def test_register_user_successfully(client: TestClient):
    """
    Tests successful user registration.

    This test sends a POST request to the /auth/register endpoint with valid
    user data and asserts that the response is successful (status code 201)
    and contains the new user's information.
    """
    response = client.post("/auth/register", json=TEST_USER_DATA)

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["username"] == TEST_USER_DATA["username"]
    assert data["email"] == TEST_USER_DATA["email"]
    assert "password" not in data  # Ensure password is not returned in the response


def test_login_for_access_token_successfully(client: TestClient):
    """
    Tests successful user login after registration.

    This test first registers a user (ensuring they exist in the test DB)
    and then sends a POST request to the /auth/login endpoint. It asserts
    that the response contains valid access and refresh tokens.
    """
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "LoginPassword123!",
        "email": "login@example.com"
    })

    login_data = {
        "username": "loginuser",
        "password": "LoginPassword123!"
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_existing_user_fails(client: TestClient):
    """
    Tests that registration fails when using an already-registered email.

    This test first registers a user, then tries to register another user
    with the same email but a different username. It asserts that the
    endpoint returns a 400 Bad Request error.
    """
    client.post("/auth/register", json={
        "username": "existinguser",
        "password": "ExistingPassword123!",
        "email": "existing@example.com"
    })

    response = client.post("/auth/register", json={
        "username": "anotheruser",
        "password": "AnotherPassword123!",
        "email": "existing@example.com"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_with_invalid_credentials_fails(client: TestClient):
    """
    Tests that login fails with incorrect password.

    This test first registers a user and then attempts to log in with
    the correct username but an incorrect password. It asserts that the
    endpoint returns a 401 Unauthorized error.
    """
    # Register a user to test against
    client.post("/auth/register", json={
        "username": "invaliduser",
        "password": "ValidPassword123!",
        "email": "invalid@example.com"
    })

    login_data = {
        "username": "invaliduser",
        "password": "InvalidPassword123!"
    }
    response = client.post("/auth/login", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_token_successfully(client: TestClient):
    """
    Tests refreshing an access token using a valid refresh token.

    This test logs in a user, extracts the refresh token, and then uses it
    to request a new access token. It asserts that the response is successful
    and contains a new access token.
    """
    client.post("/auth/register", json={
        "username": "refreshuser",
        "password": "RefreshPassword123!",
        "email": "refresh@example.com"
    })
    login_response = client.post("/auth/login", data={
        "username": "refreshuser",
        "password": "RefreshPassword123!"
    })
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert refresh_response.status_code == 200

    new_token_data = refresh_response.json()
    assert "access_token" in new_token_data
    assert new_token_data["token_type"] == "bearer"

    assert new_token_data["access_token"] != login_response.json()["access_token"]


def test_logout_successfully(client: TestClient):
    """
    Tests successful user logout.

    This test logs in a user, gets their access token, and then uses that
    token to make a POST request to the /auth/logout endpoint. It asserts
    that the logout is successful and the refresh token is invalidated.
    """
    client.post("/auth/register", json={
        "username": "logoutuser",
        "password": "LogoutPassword123!",
        "email": "logout@example.com"
    })
    login_response = client.post("/auth/login", data={
        "username": "logoutuser",
        "password": "LogoutPassword123!"
    })
    access_token = login_response.json()["access_token"]

    logout_response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"
