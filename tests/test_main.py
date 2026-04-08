from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_app_starts() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_basic_route_returns_200() -> None:
    response = client.get("/genre")
    assert response.status_code == 200
    payload = response.json()
    assert "genre" in payload
