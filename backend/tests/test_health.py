from fastapi import status


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data
    assert "environment" in data


def test_ready_endpoint(client):
    response = client.get("/ready")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "healthy"
    assert "version" in data


def test_api_v1_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
