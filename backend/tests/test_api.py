from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_genre_returns_value() -> None:
    response = client.get("/genre")
    assert response.status_code == 200
    payload = response.json()
    assert "genre" in payload
    assert isinstance(payload["genre"], str)


def test_recommend_returns_books() -> None:
    genre_payload = client.get("/genre").json()
    response = client.get(f"/recommend/{genre_payload['genre']}")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["books"]) >= 3
    assert len(payload["books"]) <= 5


def test_history_records_recommendation_calls() -> None:
    genre_payload = client.get("/genre").json()
    client.get(f"/recommend/{genre_payload['genre']}")
    response = client.get("/history")
    assert response.status_code == 200
    payload = response.json()
    assert "history" in payload
    assert isinstance(payload["history"], list)
