from fastapi import status


def test_create_feedback_success(client):
    payload = {
        "source": "Web Form",
        "customer_identifier": "cust_123",
        "feedback_text": "The latest checkout experience is remarkably intuitive and fast!",
        "category": "User Experience",
        "sentiment": "positive",
        "sentiment_score": 0.95,
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["source"] == "Web Form"
    assert data["customer_identifier"] == "cust_123"
    assert data["feedback_text"] == payload["feedback_text"]
    assert data["category"] == "User Experience"
    assert data["sentiment"] == "positive"
    assert data["sentiment_score"] == 0.95
    assert data["status"] == "new"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_feedback_validation_errors(client):
    # Empty feedback text
    res1 = client.post("/api/v1/feedback", json={"source": "Web", "feedback_text": "   "})
    assert res1.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Too short feedback text
    res2 = client.post("/api/v1/feedback", json={"source": "Web", "feedback_text": "hi"})
    assert res2.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Missing source
    res3 = client.post("/api/v1/feedback", json={"feedback_text": "Valid feedback length"})
    assert res3.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Invalid sentiment_score > 1.0
    res4 = client.post(
        "/api/v1/feedback",
        json={"source": "Web", "feedback_text": "Valid text", "sentiment_score": 1.5},
    )
    assert res4.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_feedback_by_id(client):
    create_res = client.post(
        "/api/v1/feedback",
        json={
            "source": "Email",
            "customer_identifier": "sarah@example.com",
            "feedback_text": "Shipping took 7 business days instead of the promised 2.",
            "category": "Delivery",
            "sentiment": "negative",
            "sentiment_score": 0.88,
        },
    )
    item_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/feedback/{item_id}")
    assert get_res.status_code == status.HTTP_200_OK
    data = get_res.json()
    assert data["id"] == item_id
    assert data["category"] == "Delivery"
    assert data["sentiment"] == "negative"


def test_get_missing_feedback(client):
    response = client.get("/api/v1/feedback/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


def test_list_feedback_pagination_and_filtering(client):
    # Create several feedback items
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Mobile App",
            "feedback_text": "Crash when uploading profile picture in settings.",
            "category": "Product Quality",
            "sentiment": "negative",
        },
    )
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Survey",
            "feedback_text": "Great discount during the annual sale event.",
            "category": "Pricing",
            "sentiment": "positive",
        },
    )

    # Test pagination
    list_res = client.get("/api/v1/feedback?skip=0&limit=2")
    assert list_res.status_code == status.HTTP_200_OK
    data = list_res.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 2
    assert data["total"] >= 2

    # Test category filter
    filter_res = client.get("/api/v1/feedback?category=Pricing")
    assert filter_res.status_code == status.HTTP_200_OK
    filter_data = filter_res.json()
    for item in filter_data["items"]:
        assert item["category"] == "Pricing"

    # Test sentiment filter
    sentiment_res = client.get("/api/v1/feedback?sentiment=negative")
    assert sentiment_res.status_code == status.HTTP_200_OK
    sentiment_data = sentiment_res.json()
    for item in sentiment_data["items"]:
        assert item["sentiment"] == "negative"

    # Test search query
    search_res = client.get("/api/v1/feedback?search=crash")
    assert search_res.status_code == status.HTTP_200_OK
    search_data = search_res.json()
    assert any("crash" in item["feedback_text"].lower() for item in search_data["items"])


def test_update_feedback(client):
    create_res = client.post(
        "/api/v1/feedback",
        json={
            "source": "Web Form",
            "feedback_text": "Please add dark mode theme option.",
            "category": "Feature Request",
            "sentiment": "neutral",
        },
    )
    item_id = create_res.json()["id"]

    # Update status and category
    patch_res = client.patch(
        f"/api/v1/feedback/{item_id}",
        json={"status": "resolved", "sentiment": "positive", "sentiment_score": 0.75},
    )
    assert patch_res.status_code == status.HTTP_200_OK
    data = patch_res.json()
    assert data["id"] == item_id
    assert data["status"] == "resolved"
    assert data["sentiment"] == "positive"
    assert data["sentiment_score"] == 0.75


def test_update_missing_feedback(client):
    patch_res = client.patch("/api/v1/feedback/999999", json={"status": "resolved"})
    assert patch_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_feedback(client):
    create_res = client.post(
        "/api/v1/feedback",
        json={
            "source": "API",
            "feedback_text": "Temporary feedback to be removed.",
        },
    )
    item_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/feedback/{item_id}")
    assert del_res.status_code == status.HTTP_200_OK

    # Ensure record is gone
    get_res = client.get(f"/api/v1/feedback/{item_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_delete_missing_feedback(client):
    del_res = client.delete("/api/v1/feedback/999999")
    assert del_res.status_code == status.HTTP_404_NOT_FOUND
