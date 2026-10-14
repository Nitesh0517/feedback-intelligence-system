import pytest
from app.tasks.celery_app import celery_app
from app.tasks.feedback_tasks import analyze_feedback_task, batch_analyze_feedback_task
from app.models.feedback import Feedback
from app.db.session import SessionLocal


@pytest.fixture(autouse=True)
def configure_celery_eager():
    """Ensure Celery runs tasks eagerly in-memory during tests."""
    celery_app.conf.update(
        task_always_eager=True,
        task_store_eager_result=True,
        result_backend="cache+memory://",
    )
    yield



def test_analyze_feedback_task_execution():
    db = SessionLocal()
    try:
        feedback = Feedback(
            feedback_text="The customer support team resolved my billing issue in 5 minutes! Outstanding service.",
            source="email",
            customer_identifier="cust_task_1",
            status="pending",
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        feedback_id = feedback.id
    finally:
        db.close()

    result = analyze_feedback_task.delay(feedback_id=feedback_id)
    assert result.successful()
    task_res = result.result
    assert task_res["status"] == "completed"
    assert task_res["sentiment"] == "positive"
    assert task_res["category"] == "Customer Support"

    # Verify DB updated
    db = SessionLocal()
    try:
        refreshed = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        assert refreshed.status == "analyzed"
        assert refreshed.sentiment == "positive"
        assert refreshed.category == "Customer Support"
    finally:
        db.close()


def test_analyze_feedback_task_duplicate_prevention():
    db = SessionLocal()
    try:
        feedback = Feedback(
            feedback_text="System was already processed previously.",
            source="portal",
            customer_identifier="cust_dup_1",
            status="analyzed",
            sentiment="positive",
            sentiment_score=0.9,
            category="General",
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        feedback_id = feedback.id
    finally:
        db.close()

    result = analyze_feedback_task.delay(feedback_id=feedback_id)
    assert result.successful()
    assert result.result.get("note") == "already_analyzed"


def test_batch_analyze_feedback_task():
    db = SessionLocal()
    try:
        fb1 = Feedback(
            feedback_text="App crashes constantly on startup",
            source="mobile_app",
            customer_identifier="cust_batch_1",
            status="pending",
        )
        fb2 = Feedback(
            feedback_text="Pricing is too expensive for small teams",
            source="web",
            customer_identifier="cust_batch_2",
            status="pending",
        )
        db.add_all([fb1, fb2])
        db.commit()
    finally:
        db.close()

    result = batch_analyze_feedback_task.delay(limit=10)
    assert result.successful()
    task_res = result.result
    assert task_res["status"] == "completed"
    assert task_res["processed_count"] >= 2


def test_async_feedback_analyze_endpoints(client):
    # 1. Create a feedback item
    create_resp = client.post(
        "/api/v1/feedback",
        json={
            "feedback_text": "Terrible customer service, awful response time and broken app!",
            "source": "api",
            "customer_identifier": "cust_async_api",
        },
    )
    assert create_resp.status_code == 201
    feedback_id = create_resp.json()["id"]

    # 2. Trigger async analysis endpoint
    async_resp = client.post(f"/api/v1/feedback/{feedback_id}/analyze-async")
    assert async_resp.status_code == 202
    data = async_resp.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # 3. Check task status endpoint
    task_resp = client.get(f"/api/v1/tasks/{task_id}")
    assert task_resp.status_code == 200
    task_data = task_resp.json()
    assert task_data["task_id"] == task_id
    assert task_data["ready"] is True
    assert task_data["successful"] is True
    assert task_data["result"]["status"] == "completed"
    assert task_data["result"]["sentiment"] == "negative"


def test_async_feedback_analyze_not_found(client):
    response = client.post("/api/v1/feedback/99999/analyze-async")
    assert response.status_code == 404


def test_batch_analyze_async_endpoint(client):
    response = client.post("/api/v1/feedback/batch-analyze-async?limit=5")
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # Check task status
    task_resp = client.get(f"/api/v1/tasks/{task_id}")
    assert task_resp.status_code == 200
    assert task_resp.json()["ready"] is True
