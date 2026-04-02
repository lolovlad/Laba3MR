from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_recommend() -> None:
    payload = {
        "user_id": 1,
        "top_k": 5,
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == 1
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) == 5
