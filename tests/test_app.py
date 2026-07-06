from fastapi.testclient import TestClient

from src.app import app


def test_unregister_participant_removes_email_from_activity():
    client = TestClient(app)

    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }

    updated = client.get("/activities")
    assert "michael@mergington.edu" not in updated.json()["Chess Club"]["participants"]
