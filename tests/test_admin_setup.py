import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User

ADMIN_SETUP_DATA = {
    "username": "initial_admin",
    "password": "Password123!",
    "email": "initial_admin@example.com",
}


def test_create_first_admin_successfully(client: TestClient, db_session: Session):
    """
    Test the successful creation of the first admin user.
    This should only happen when no users exist in the database.
    """
    db_session.query(User).delete()
    db_session.commit()

    response = client.post("/admin-setup", json=ADMIN_SETUP_DATA)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["username"] == ADMIN_SETUP_DATA["username"]
    assert response_data["email"] == ADMIN_SETUP_DATA["email"]
    assert response_data["is_admin"] is True

    created_user = db_session.query(User).filter_by(username=ADMIN_SETUP_DATA["username"]).first()
    assert created_user is not None
    assert created_user.is_admin is True


def test_create_first_admin_forbidden(client: TestClient, db_session: Session):
    """
    Test that creating a second admin user is forbidden.
    The endpoint should return a 403 Forbidden error.
    """
    existing_admin_data = {
        "username": "existing_admin",
        "email": "existing_admin@example.com",
        "hashed_password": "some_hashed_password",
        "is_admin": True,
    }
    existing_admin = User(**existing_admin_data)
    db_session.add(existing_admin)
    db_session.commit()

    new_admin_data = {
        "username": "second_admin",
        "password": "NewPassword123!",
        "email": "second_admin@example.com",
    }
    response = client.post("/admin-setup", json=new_admin_data)

    assert response.status_code == 403
    assert "detail" in response.json()
    assert response.json()["detail"] == "Admin user already exists. This endpoint is for initial setup only."

    new_user = db_session.query(User).filter_by(username=new_admin_data["username"]).first()
    assert new_user is None