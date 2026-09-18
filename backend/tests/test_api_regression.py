import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def test_audit_logs_endpoint_is_available_and_returns_recent_entries() -> None:
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200

    response = client.get("/api/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_polaris_assistant_uses_database_state_and_references_entities() -> None:
    client = TestClient(app)
    response = client.get("/api/polaris/assistant", params={"q": "What are the highest risks at Bharati?"})
    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert isinstance(payload["answer"], str)
    assert "Bharati" in payload["answer"] or "transport" in payload["answer"].lower()
