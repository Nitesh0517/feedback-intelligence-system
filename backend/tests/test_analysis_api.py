from fastapi import status


def test_analyze_existing_feedback_endpoint(client):
    # Create an unanalyzed feedback item
    create_res = client.post(
        "/api/v1/feedback",
        json={
            "source": "Web Form",
            "customer_identifier": "alice@corp.com",
            "feedback_text": "The shipping delivery time was exceptionally fast and the package was spotless!",
        },
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    item_id = create_res.json()["id"]

    # Trigger analysis via API
    analyze_res = client.post(f"/api/v1/feedback/{item_id}/analyze")
    assert analyze_res.status_code == status.HTTP_200_OK
    data = analyze_res.json()

    assert data["id"] == item_id
    assert data["status"] == "analyzed"
    assert data["sentiment"] == "positive"
    assert data["sentiment_score"] > 0.50
    assert data["category"] == "Delivery"

    # Verify retrieval from database reflects persisted values
    get_res = client.get(f"/api/v1/feedback/{item_id}")
    assert get_res.status_code == status.HTTP_200_OK
    get_data = get_res.json()
    assert get_data["status"] == "analyzed"
    assert get_data["sentiment"] == "positive"
    assert get_data["category"] == "Delivery"


def test_analyze_negative_feedback_persistence(client):
    create_res = client.post(
        "/api/v1/feedback",
        json={
            "source": "Email",
            "customer_identifier": "bob@acme.org",
            "feedback_text": "The support agent was very rude and unhelpful when dealing with my ticket.",
        },
    )
    item_id = create_res.json()["id"]

    analyze_res = client.post(f"/api/v1/feedback/{item_id}/analyze")
    assert analyze_res.status_code == status.HTTP_200_OK
    data = analyze_res.json()

    assert data["sentiment"] == "negative"
    assert data["category"] == "Customer Support"


def test_analyze_missing_feedback_returns_404(client):
    res = client.post("/api/v1/feedback/999999/analyze")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in res.json()["detail"].lower()


def test_batch_analyze_endpoint(client):
    # Ingest multiple unanalyzed feedback items
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Survey",
            "feedback_text": "The subscription fee is way too expensive for what it offers.",
        },
    )
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Mobile App",
            "feedback_text": "Please add an option to customize the notification sounds.",
        },
    )

    batch_res = client.post("/api/v1/feedback/batch-analyze?limit=10")
    assert batch_res.status_code == status.HTTP_200_OK
    batch_data = batch_res.json()
    assert batch_data["processed_count"] >= 2
    assert batch_data["error_count"] == 0
