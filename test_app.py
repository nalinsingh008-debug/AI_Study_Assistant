from fastapi.testclient import TestClient
from app.main import app, predictor
from app.models import StudySession

client = TestClient(app)

def test_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Study Assistant Pro" in response.text

def test_session_validation_rejects_empty_subject():
    try:
        StudySession("", 1, 1, "2026-11-14").validate()
        assert False, "Expected validation error"
    except ValueError:
        assert True

def test_predictor_returns_score_in_range():
    score = predictor.predict_score(2, 4)
    assert 0 <= score <= 100

def test_predictor_rejects_negative_hours():
    try:
        predictor.predict_score(-1, 2)
        assert False, "Expected validation error"
    except ValueError:
        assert True

def test_create_session_endpoint():
    response = client.post("/sessions", json={
        "subject": "Pytest Demo", "study_hours": 1.5,
        "tasks_completed": 3, "session_date": "2026-11-14"
    })
    assert response.status_code == 200
    assert response.json()["id"] > 0

def test_analytics_endpoint():
    response = client.get("/analytics")
    assert response.status_code == 200
    assert "total_sessions" in response.json()
