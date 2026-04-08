"""
API tests – run without a live MongoDB instance.
The app gracefully falls back to file-based storage when MongoDB is unavailable.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ── helpers ───────────────────────────────────────────────────────────────────

def _register_and_login(username: str, password: str = "testpass") -> str:
    """Sign up (ignore if already exists) and return a bearer token."""
    client.post("/signup", json={"username": username, "password": password})
    resp = client.post("/login", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── basic health ──────────────────────────────────────────────────────────────

def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── genre & recommendations ───────────────────────────────────────────────────

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
    assert 3 <= len(payload["books"]) <= 5


# ── auth ──────────────────────────────────────────────────────────────────────

def test_signup_and_login() -> None:
    token = _register_and_login("testuser_auth")
    assert isinstance(token, str) and len(token) > 0


def test_login_wrong_password_returns_401() -> None:
    _register_and_login("testuser_wrongpw")
    resp = client.post("/login", json={"username": "testuser_wrongpw", "password": "wrongpass"})
    assert resp.status_code == 401


def test_duplicate_signup_returns_400() -> None:
    _register_and_login("testuser_dup")
    resp = client.post("/signup", json={"username": "testuser_dup", "password": "testpass"})
    assert resp.status_code == 400


# ── per-user history isolation ────────────────────────────────────────────────

def test_history_is_empty_without_token() -> None:
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json()["history"] == []


def test_history_is_user_specific() -> None:
    token_a = _register_and_login("hist_user_a")
    token_b = _register_and_login("hist_user_b")

    # User A makes a recommendation request
    genre = client.get("/genre").json()["genre"]
    client.get(f"/recommend/{genre}", headers={"Authorization": f"Bearer {token_a}"})

    # User A should have history
    hist_a = client.get("/history", headers={"Authorization": f"Bearer {token_a}"}).json()
    assert len(hist_a["history"]) >= 1

    # User B should have NO history (different user)
    hist_b = client.get("/history", headers={"Authorization": f"Bearer {token_b}"}).json()
    assert hist_b["history"] == []


def test_history_records_recommendation_calls() -> None:
    token = _register_and_login("hist_user_record")
    genre = client.get("/genre").json()["genre"]
    client.get(f"/recommend/{genre}", headers={"Authorization": f"Bearer {token}"})
    response = client.get("/history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert "history" in payload
    assert len(payload["history"]) >= 1
    assert payload["history"][0]["genre"] == genre
