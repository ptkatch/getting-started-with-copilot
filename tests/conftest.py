import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing a TestClient for API testing."""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Fixture that snapshots the activities state before each test
    and resets it after the test completes.
    Ensures test isolation despite in-memory data store.
    """
    # Snapshot the original state
    original_state = {
        activity_name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy(),
        }
        for activity_name, details in activities.items()
    }

    yield  # Run the test

    # Restore the original state
    activities.clear()
    for activity_name, original_details in original_state.items():
        activities[activity_name] = original_details
