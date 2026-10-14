import pytest
from fastapi import status

from app.core.rate_limit import is_rate_limit_exceeded, clear_rate_limits
from app.db.session import SessionLocal
from app.models.user import User


def test_viewer_permissions(unauthenticated_client, viewer_headers):
    # 1. Viewer CAN list feedback
    res_list = unauthenticated_client.get("/api/v1/feedback", headers=viewer_headers)
    assert res_list.status_code == status.HTTP_200_OK

    # 2. Viewer CAN access analytics
    res_analytics = unauthenticated_client.get("/api/v1/analytics/overview", headers=viewer_headers)
    assert res_analytics.status_code == status.HTTP_200_OK

    # 3. Viewer CANNOT create feedback
    res_create = unauthenticated_client.post(
        "/api/v1/feedback",
        headers=viewer_headers,
        json={"feedback_text": "Viewer test feedback", "source": "web"},
    )
    assert res_create.status_code == status.HTTP_403_FORBIDDEN

    # 4. Viewer CANNOT delete feedback
    res_delete = unauthenticated_client.delete("/api/v1/feedback/1", headers=viewer_headers)
    assert res_delete.status_code == status.HTTP_403_FORBIDDEN

    # 5. Viewer CANNOT analyze feedback
    res_analyze = unauthenticated_client.post("/api/v1/feedback/1/analyze", headers=viewer_headers)
    assert res_analyze.status_code == status.HTTP_403_FORBIDDEN

    # 6. Viewer CANNOT access user management
    res_users = unauthenticated_client.get("/api/v1/users", headers=viewer_headers)
    assert res_users.status_code == status.HTTP_403_FORBIDDEN


def test_analyst_permissions(unauthenticated_client, analyst_headers):
    # 1. Analyst CAN create feedback
    res_create = unauthenticated_client.post(
        "/api/v1/feedback",
        headers=analyst_headers,
        json={
            "feedback_text": "Analyst created feedback for test verification.",
            "source": "api",
            "customer_identifier": "analyst_user",
        },
    )
    assert res_create.status_code == status.HTTP_201_CREATED
    feedback_id = res_create.json()["id"]

    # 2. Analyst CAN analyze feedback
    res_analyze = unauthenticated_client.post(
        f"/api/v1/feedback/{feedback_id}/analyze",
        headers=analyst_headers,
    )
    assert res_analyze.status_code == status.HTTP_200_OK

    # 3. Analyst CAN update feedback
    res_update = unauthenticated_client.patch(
        f"/api/v1/feedback/{feedback_id}",
        headers=analyst_headers,
        json={"category": "Product Quality"},
    )
    assert res_update.status_code == status.HTTP_200_OK

    # 4. Analyst CANNOT delete feedback
    res_delete = unauthenticated_client.delete(
        f"/api/v1/feedback/{feedback_id}",
        headers=analyst_headers,
    )
    assert res_delete.status_code == status.HTTP_403_FORBIDDEN

    # 5. Analyst CANNOT access user management
    res_users = unauthenticated_client.get("/api/v1/users", headers=analyst_headers)
    assert res_users.status_code == status.HTTP_403_FORBIDDEN


def test_admin_user_management(unauthenticated_client, admin_headers):
    # 1. Admin CAN list users
    res = unauthenticated_client.get("/api/v1/users", headers=admin_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "items" in data
    assert data["total"] >= 3

    # Find the viewer user to test role and status updates
    db = SessionLocal()
    try:
        viewer = db.query(User).filter(User.email == "viewer@test.com").first()
        viewer_id = viewer.id
    finally:
        db.close()

    # 2. Admin CAN update user role
    role_res = unauthenticated_client.patch(
        f"/api/v1/users/{viewer_id}/role",
        headers=admin_headers,
        json={"role": "analyst"},
    )
    assert role_res.status_code == status.HTTP_200_OK
    assert role_res.json()["role"] == "analyst"

    # Revert back to viewer
    unauthenticated_client.patch(
        f"/api/v1/users/{viewer_id}/role",
        headers=admin_headers,
        json={"role": "viewer"},
    )


def test_admin_safeguards_last_admin_protection(unauthenticated_client, admin_headers):
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@test.com").first()
        admin_id = admin.id
    finally:
        db.close()

    # 1. Admin CANNOT demote the last remaining active administrator
    demote_res = unauthenticated_client.patch(
        f"/api/v1/users/{admin_id}/role",
        headers=admin_headers,
        json={"role": "viewer"},
    )
    assert demote_res.status_code == status.HTTP_400_BAD_REQUEST
    assert "last remaining active administrator" in demote_res.json()["detail"].lower()

    # 2. Admin CANNOT deactivate their own account
    deactivate_res = unauthenticated_client.patch(
        f"/api/v1/users/{admin_id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert deactivate_res.status_code == status.HTTP_400_BAD_REQUEST

    # 3. Admin CANNOT delete their own account
    delete_res = unauthenticated_client.delete(
        f"/api/v1/users/{admin_id}",
        headers=admin_headers,
    )
    assert delete_res.status_code == status.HTTP_400_BAD_REQUEST


def test_rate_limiting_sliding_window():
    clear_rate_limits()
    test_key = "test-client-ip:test-scope"
    limit = 3

    # Calls 1, 2, 3 should be permitted
    for _ in range(limit):
        exceeded, remaining, _ = is_rate_limit_exceeded(test_key, limit=limit, window_seconds=60)
        assert not exceeded

    # Call 4 should exceed the limit
    exceeded, remaining, retry_after = is_rate_limit_exceeded(test_key, limit=limit, window_seconds=60)
    assert exceeded
    assert retry_after > 0


def test_security_headers_present(unauthenticated_client):
    response = unauthenticated_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
