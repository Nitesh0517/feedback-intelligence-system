import pytest
from fastapi import status
from app.processing.cleaner import clean_text, tokenize, validate_text
from app.intelligence.sentiment_analyzer import get_sentiment_analyzer
from app.intelligence.categorizer import get_categorizer
from app.tasks.feedback_tasks import analyze_feedback_task


def test_cleaner_and_sentiment_edge_cases():
    """Tests edge cases: emojis, special characters, and boundary lengths."""
    # Text with emojis and punctuation
    text = "Great product! 😀 Works smoothly, but was somewhat delayed. 👍"
    cleaned = clean_text(text)
    assert "Great product!" in cleaned
    
    analyzer = get_sentiment_analyzer()
    res = analyzer.analyze(text)
    assert res.sentiment in ["positive", "neutral", "negative"]
    assert 0.0 <= res.confidence_score <= 1.0
    assert -1.0 <= res.compound_score <= 1.0


def test_very_long_feedback_boundary():
    """Tests feedback near maximum allowed character boundary (up to 10,000 chars)."""
    long_text = "The product is great. " * 300  # ~6600 chars
    validated = validate_text(long_text, max_length=10000)
    assert len(validated) > 6000
    
    analyzer = get_sentiment_analyzer()
    res = analyzer.analyze(validated)
    assert res.sentiment == "positive"
    
    # Exceeding 10,000 chars raises ValueError
    too_long = "a" * 10005
    with pytest.raises(ValueError, match="exceeds maximum length"):
        validate_text(too_long, max_length=10000)


def test_categorizer_multiword_phrase_precedence():
    """Tests that strong phrase cues override competing single keywords."""
    # Contains "price" (Pricing keyword) and "user interface" (UX phrase)
    text = "The price was fine, but the user interface was very hard to navigate."
    categorizer = get_categorizer()
    cat_res = categorizer.categorize(text)
    assert cat_res.category == "User Experience"
    assert "user interface" in cat_res.matched_features


def test_api_sorting_endpoints(client):
    """Tests the GET /api/v1/feedback sorting endpoints via HTTP."""
    # Seed 2 feedback items with different scores
    client.post("/api/v1/feedback", json={
        "source": "Web",
        "feedback_text": "First sorting test item",
        "sentiment": "negative",
        "sentiment_score": 0.15,
    })
    client.post("/api/v1/feedback", json={
        "source": "Mobile",
        "feedback_text": "Second sorting test item",
        "sentiment": "positive",
        "sentiment_score": 0.85,
    })

    # Sort ASC
    res_asc = client.get("/api/v1/feedback?sort_by=sentiment_score&order=asc&limit=10")
    assert res_asc.status_code == status.HTTP_200_OK
    items_asc = res_asc.json()["items"]
    scores_asc = [i["sentiment_score"] for i in items_asc if i.get("sentiment_score") is not None]
    assert scores_asc == sorted(scores_asc)

    # Sort DESC
    res_desc = client.get("/api/v1/feedback?sort_by=sentiment_score&order=desc&limit=10")
    assert res_desc.status_code == status.HTTP_200_OK
    items_desc = res_desc.json()["items"]
    scores_desc = [i["sentiment_score"] for i in items_desc if i.get("sentiment_score") is not None]
    assert scores_desc == sorted(scores_desc, reverse=True)


def test_tampered_and_malformed_auth_headers(unauthenticated_client):
    """Tests that malformed or tampered Authorization headers are rejected with HTTP 401."""
    # Malformed token string
    res1 = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )
    assert res1.status_code == status.HTTP_401_UNAUTHORIZED
    assert "credentials" in res1.json()["detail"].lower()

    # Header without Bearer prefix
    res2 = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert res2.status_code == status.HTTP_401_UNAUTHORIZED

    # Empty bearer header
    res3 = unauthenticated_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer "},
    )
    assert res3.status_code == status.HTTP_401_UNAUTHORIZED


def test_task_status_for_invalid_id(client):
    """Tests GET /api/v1/tasks/{task_id} behavior with an unknown task ID."""
    res = client.get("/api/v1/tasks/nonexistent-task-id-12345")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["task_id"] == "nonexistent-task-id-12345"
    assert data["ready"] is False
    assert data["successful"] is None
