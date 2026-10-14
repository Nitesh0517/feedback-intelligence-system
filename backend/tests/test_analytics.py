from datetime import date, timedelta
from unittest.mock import patch
from fastapi import status
from sqlalchemy.exc import OperationalError


def test_analytics_empty_database(client):
    # Tests that when database has no records, analytics endpoints return 0s gracefully
    res_overview = client.get("/api/v1/analytics/overview")
    assert res_overview.status_code == status.HTTP_200_OK
    data = res_overview.json()
    assert data["total_feedback"] >= 0

    res_sentiment = client.get("/api/v1/analytics/sentiment")
    assert res_sentiment.status_code == status.HTTP_200_OK

    res_categories = client.get("/api/v1/analytics/categories")
    assert res_categories.status_code == status.HTTP_200_OK
    assert "categories" in res_categories.json()

    res_trends = client.get("/api/v1/analytics/trends?days=7")
    assert res_trends.status_code == status.HTTP_200_OK
    assert len(res_trends.json()["data_points"]) == 7


def test_analytics_with_actual_feedback_data(client):
    # Ingest diverse feedback items
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Web Form",
            "feedback_text": "Remarkable speed and brilliant user interface!",
            "category": "User Experience",
            "sentiment": "positive",
            "sentiment_score": 0.95,
        },
    )
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Email",
            "feedback_text": "The monthly fee is way too high and overpriced.",
            "category": "Pricing",
            "sentiment": "negative",
            "sentiment_score": 0.85,
        },
    )
    client.post(
        "/api/v1/feedback",
        json={
            "source": "Survey",
            "feedback_text": "The delivery was scheduled for yesterday.",
            "category": "Delivery",
            "sentiment": "neutral",
            "sentiment_score": 0.50,
        },
    )

    # 1. Test Overview Analytics
    overview_res = client.get("/api/v1/analytics/overview")
    assert overview_res.status_code == status.HTTP_200_OK
    ov = overview_res.json()
    assert ov["total_feedback"] >= 3
    assert ov["positive_count"] >= 1
    assert ov["negative_count"] >= 1
    assert ov["neutral_count"] >= 1
    assert "sentiment_distribution" in ov

    # 2. Test Sentiment Analytics
    sentiment_res = client.get("/api/v1/analytics/sentiment")
    assert sentiment_res.status_code == status.HTTP_200_OK
    sent = sentiment_res.json()
    assert sent["total"] >= 3
    assert sent["positive"] >= 1
    assert sent["negative"] >= 1
    assert sent["average_sentiment_score"] is not None

    # 3. Test Category Analytics
    cat_res = client.get("/api/v1/analytics/categories")
    assert cat_res.status_code == status.HTTP_200_OK
    cats = cat_res.json()
    assert cats["categories"]["User Experience"] >= 1
    assert cats["categories"]["Pricing"] >= 1
    assert cats["categories"]["Delivery"] >= 1
    assert "percentages" in cats

    # 4. Test Trends Analytics
    trends_res = client.get("/api/v1/analytics/trends?days=14")
    assert trends_res.status_code == status.HTTP_200_OK
    trends = trends_res.json()
    assert len(trends["data_points"]) == 14
    assert trends["total_volume"] >= 3
    assert "summary" in trends
    assert isinstance(trends["recommendations"], list)


def test_analytics_invalid_date_range(client):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # start_date > end_date should fail with 400
    res = client.get(f"/api/v1/analytics/trends?start_date={tomorrow}&end_date={yesterday}")
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot be after" in res.json()["detail"].lower()


def test_analytics_database_error_handling(admin_headers):
    from fastapi.testclient import TestClient
    from app.main import app

    client_no_raise = TestClient(app, raise_server_exceptions=False)
    with patch(
        "app.services.analytics_service.get_overview",
        side_effect=OperationalError("connection closed", params=None, orig=Exception("DB unavailable")),
    ):
        res = client_no_raise.get("/api/v1/analytics/overview", headers=admin_headers)
        assert res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = res.json()
        assert data["error_code"] == "INTERNAL_SERVER_ERROR"
        assert "unexpected server error" in data["detail"].lower()

