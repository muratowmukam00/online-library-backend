import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from app.main import app
from app.core.config import get_settings
from app.core.database import Base, get_db
from app.models import User
from app.core.security import create_access_token, get_password_hash

load_dotenv('.env.test')


def create_test_user(db: Session, username: str, email: str, password: str, is_admin: bool = False):
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    settings = get_settings()
    test_db_url = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    test_engine = create_engine(test_db_url)
    yield test_engine


@pytest.fixture(scope="function", autouse=True)
def clean_db(test_db_setup):
    Base.metadata.drop_all(bind=test_db_setup)
    Base.metadata.create_all(bind=test_db_setup)
    yield
    Base.metadata.drop_all(bind=test_db_setup)


@pytest.fixture(scope="function")
def db_session(test_db_setup):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_setup)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def admin_client(client: TestClient, db_session: Session):
    user = create_test_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        password="password",
        is_admin=True,
    )
    token = create_access_token({"sub": str(user.username), "is_admin": True})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def authenticated_client(client: TestClient, db_session: Session):
    user = create_test_user(
        db=db_session,
        username="user",
        email="user@example.com",
        password="password",
        is_admin=False,
    )
    token = create_access_token({"sub": str(user.username), "is_admin": False})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def admin_headers(db_session: Session):
    user = create_test_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        password="password",
        is_admin=True,
    )
    token = create_access_token({"sub": str(user.id), "is_admin": True})
    return {"Authorization": f"Bearer {token}"}