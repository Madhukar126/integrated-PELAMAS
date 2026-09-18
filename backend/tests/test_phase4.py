import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def test_phase4_map_api_is_available() -> None:
    client = TestClient(app)
    response = client.get("/api/phase4/map")
    assert response.status_code == 200
    payload = response.json()
    assert "stations" in payload
    assert "routes" in payload
    assert "layers" in payload


def test_phase4_notifications_api_is_available() -> None:
    client = TestClient(app)
    response = client.get("/api/phase4/notifications")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    if payload:
        assert "title" in payload[0]


def test_phase4_demo_reset_api_is_available() -> None:
    client = TestClient(app)
    response = client.post("/api/phase4/demo/reset")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "reset"
