import os
import pytest
from fastapi.testclient import TestClient

# Ensure test configuration is used
os.environ["DATABASE_URL"] = "sqlite:///./test_feedback.db"
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-unit-testing-min-32-chars-long"

from app.main import app
from app.db.session import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Create standard test users for tests
        admin = User(
            name="Test Admin",
            email="admin@test.com",
            hashed_password=get_password_hash("AdminPass123!"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        analyst = User(
            name="Test Analyst",
            email="analyst@test.com",
            hashed_password=get_password_hash("AnalystPass123!"),
            role=UserRole.ANALYST.value,
            is_active=True,
        )
        viewer = User(
            name="Test Viewer",
            email="viewer@test.com",
            hashed_password=get_password_hash("ViewerPass123!"),
            role=UserRole.VIEWER.value,
            is_active=True,
        )
        db.add_all([admin, analyst, viewer])
        db.commit()
    finally:
        db.close()

    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_feedback.db"):
        try:
            os.remove("./test_feedback.db")
        except Exception:
            pass


@pytest.fixture
def admin_headers():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@test.com").first()
        token = create_access_token(subject=user.id, role=user.role, name=user.name)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


@pytest.fixture
def analyst_headers():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "analyst@test.com").first()
        token = create_access_token(subject=user.id, role=user.role, name=user.name)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


@pytest.fixture
def viewer_headers():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "viewer@test.com").first()
        token = create_access_token(subject=user.id, role=user.role, name=user.name)
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    # Module-level client authenticated as admin by default to maintain backwards compatibility
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@test.com").first()
        token = create_access_token(subject=admin.id, role="admin", name="Test Admin")
    finally:
        db.close()

    with TestClient(app) as test_client:
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client


@pytest.fixture
def unauthenticated_client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
