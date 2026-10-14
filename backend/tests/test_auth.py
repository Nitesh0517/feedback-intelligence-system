import pytest
from datetime import timedelta
from fastapi import status

from app.core.security import create_access_token


def test_successful_user_registration(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password": "SecurePassword123!",
            "role": "analyst",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "jane.doe@example.com"
    assert data["user"]["role"] == "analyst"
    assert "hashed_password" not in data["user"]


def test_duplicate_registration_returns_409(unauthenticated_client):
    # Second registration with the same email
    response = unauthenticated_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate User",
            "email": "jane.doe@example.com",
            "password": "AnotherPassword123!",
            "role": "viewer",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["detail"].lower()


def test_public_registration_cannot_create_admin(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Malicious Admin",
            "email": "hacker@example.com",
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_weak_password_validation(unauthenticated_client):
    # Too short
    res_short = unauthenticated_client.post(
        "/api/v1/auth/register",
        json={"name": "Weak", "email": "weak1@example.com", "password": "abc"},
    )
    assert res_short.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # No digits
    res_no_num = unauthenticated_client.post(
        "/api/v1/auth/register",
        json={"name": "Weak", "email": "weak2@example.com", "password": "NoDigitsAtAll!"},
    )
    assert res_no_num.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_successful_login(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={
            "email": "jane.doe@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "jane.doe@example.com"


def test_login_invalid_password(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={
            "email": "jane.doe@example.com",
            "password": "WrongPassword999!",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_login_nonexistent_email_returns_identical_401(unauthenticated_client):
    # Protect against account enumeration attacks
    response = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent_ghost@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_auth_me_authenticated(unauthenticated_client):
    # Login to get valid token
    login_res = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    token = login_res.json()["access_token"]

    me_res = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == status.HTTP_200_OK
    data = me_res.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


def test_auth_me_unauthenticated(unauthenticated_client):
    res = unauthenticated_client.get("/api/v1/auth/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_expired_token_rejected(unauthenticated_client):
    # Generate token that expired 10 minutes ago
    expired_token = create_access_token(
        subject="admin@test.com",
        role="admin",
        expires_delta=timedelta(minutes=-10),
    )
    res = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "expired" in res.json()["detail"].lower()


def test_logout(unauthenticated_client):
    login_res = unauthenticated_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    token = login_res.json()["access_token"]

    logout_res = unauthenticated_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_res.status_code == status.HTTP_200_OK
    assert "logged out" in logout_res.json()["detail"].lower()

    # Verify that the revoked token can no longer access authenticated endpoints
    subsequent_res = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert subsequent_res.status_code == status.HTTP_401_UNAUTHORIZED
    assert "revoked" in subsequent_res.json()["detail"].lower()
