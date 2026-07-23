"""
Comprehensive tests for the FastAPI Activities Management System.
Each test follows the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


# ============================================================================
# GET / - Redirect Tests
# ============================================================================

def test_root_redirects_to_index(client):
    """
    Arrange: Test client ready
    Act: Make GET request to root path
    Assert: Response is a redirect (307/308) to /static/index.html
    """
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [307, 308]
    assert "/static/index.html" in response.headers.get("location", "")


# ============================================================================
# GET /activities - Endpoint Tests
# ============================================================================

def test_get_activities_returns_all_activities(client, fresh_activities):
    """
    Arrange: Test client ready
    Act: Make GET request to /activities
    Assert: Response is 200 and contains activities dictionary
    """
    response = client.get("/activities")
    assert response.status_code == 200
    activities_data = response.json()
    assert isinstance(activities_data, dict)
    assert len(activities_data) > 0


def test_get_activities_response_structure(client, fresh_activities):
    """
    Arrange: Test client ready
    Act: Make GET request to /activities
    Assert: Each activity has required fields (description, schedule, max_participants, participants)
    """
    response = client.get("/activities")
    assert response.status_code == 200
    activities_data = response.json()

    for activity_name, activity_details in activities_data.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_details
        assert "schedule" in activity_details
        assert "max_participants" in activity_details
        assert "participants" in activity_details
        assert isinstance(activity_details["participants"], list)


def test_get_activities_non_empty(client, fresh_activities):
    """
    Arrange: Test client ready
    Act: Make GET request to /activities
    Assert: Activities list is not empty
    """
    response = client.get("/activities")
    activities_data = response.json()
    assert len(activities_data) > 0
    # Verify at least one activity exists
    first_activity = next(iter(activities_data.values()))
    assert first_activity is not None


# ============================================================================
# POST /activities/{activity_name}/signup - Registration Tests
# ============================================================================

def test_signup_new_participant_success(client, fresh_activities):
    """
    Arrange: Get an activity and prepare a new email for signup
    Act: POST signup request with activity name and email
    Assert: Response is 200, participant is added to the activity
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    new_email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] is not None
    
    # Verify participant was added
    updated_activities = client.get("/activities").json()
    assert new_email in updated_activities[activity_name]["participants"]
    assert len(updated_activities[activity_name]["participants"]) == initial_count + 1


def test_signup_nonexistent_activity_returns_404(client, fresh_activities):
    """
    Arrange: Prepare request for non-existent activity
    Act: POST signup request for activity that doesn't exist
    Assert: Response is 404 with appropriate error message
    """
    # Arrange
    fake_activity = "NonExistentActivity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{fake_activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student_returns_400(client, fresh_activities):
    """
    Arrange: Sign up a student first, then attempt to sign up the same student again
    Act: POST signup twice with same email
    Assert: Second attempt returns 400 (Bad Request)
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    existing_participant = activities[activity_name]["participants"][0]

    # Act - Try to sign up someone already registered
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_participant}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_decrements_available_spots(client, fresh_activities):
    """
    Arrange: Get activity with current spot count
    Act: Sign up a new participant
    Assert: Available spots decremented by 1
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    initial_spots = activities[activity_name]["max_participants"] - len(activities[activity_name]["participants"])
    new_email = "newstudent123@mergington.edu"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    updated_activities = client.get("/activities").json()
    new_spots = updated_activities[activity_name]["max_participants"] - len(updated_activities[activity_name]["participants"])
    assert new_spots == initial_spots - 1


def test_signup_multiple_different_students(client, fresh_activities):
    """
    Arrange: Prepare to sign up two different students to same activity
    Act: Sign up both students sequentially
    Assert: Both students appear in participants list
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    email1 = "student1_test@mergington.edu"
    email2 = "student2_test@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})

    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    updated_activities = client.get("/activities").json()
    assert email1 in updated_activities[activity_name]["participants"]
    assert email2 in updated_activities[activity_name]["participants"]
    assert len(updated_activities[activity_name]["participants"]) == initial_count + 2


# ============================================================================
# DELETE /activities/{activity_name}/signup - Unregistration Tests
# ============================================================================

def test_unregister_existing_participant_success(client, fresh_activities):
    """
    Arrange: Get an activity with existing participants
    Act: DELETE signup for an existing participant
    Assert: Participant is removed from the activity, response is 200
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    participant_to_remove = activities[activity_name]["participants"][0]
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": participant_to_remove}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] is not None
    
    # Verify participant was removed
    updated_activities = client.get("/activities").json()
    assert participant_to_remove not in updated_activities[activity_name]["participants"]
    assert len(updated_activities[activity_name]["participants"]) == initial_count - 1


def test_unregister_nonexistent_activity_returns_404(client, fresh_activities):
    """
    Arrange: Prepare request for non-existent activity
    Act: DELETE signup from activity that doesn't exist
    Assert: Response is 404
    """
    # Arrange
    fake_activity = "NonExistentActivity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{fake_activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up_returns_404(client, fresh_activities):
    """
    Arrange: Get an activity and prepare email of student not in it
    Act: DELETE signup for student not in the activity
    Assert: Response is 404
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    non_participant_email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": non_participant_email}
    )

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_unregister_increments_available_spots(client, fresh_activities):
    """
    Arrange: Get activity with current spot count including a participant
    Act: Remove that participant
    Assert: Available spots incremented by 1
    """
    # Arrange
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    participant_to_remove = activities[activity_name]["participants"][0]
    initial_spots = activities[activity_name]["max_participants"] - len(activities[activity_name]["participants"])

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": participant_to_remove})

    # Assert
    updated_activities = client.get("/activities").json()
    new_spots = updated_activities[activity_name]["max_participants"] - len(updated_activities[activity_name]["participants"])
    assert new_spots == initial_spots + 1


def test_unregister_preserves_other_participants(client, fresh_activities):
    """
    Arrange: Get activity with multiple participants
    Act: Remove one participant
    Assert: Other participants remain unchanged
    """
    # Arrange
    activities = client.get("/activities").json()
    # Find an activity with at least 2 participants
    activity_name = None
    for name, activity_data in activities.items():
        if len(activity_data["participants"]) >= 2:
            activity_name = name
            break
    
    if activity_name is None:
        # If no activity has 2+ participants, add them first
        activity_name = list(activities.keys())[0]
        client.post(f"/activities/{activity_name}/signup", params={"email": "temp1@mergington.edu"})
        client.post(f"/activities/{activity_name}/signup", params={"email": "temp2@mergington.edu"})
        activities = client.get("/activities").json()

    participant_to_remove = activities[activity_name]["participants"][0]
    other_participants = activities[activity_name]["participants"][1:]

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": participant_to_remove})

    # Assert
    updated_activities = client.get("/activities").json()
    remaining_participants = updated_activities[activity_name]["participants"]
    for other_participant in other_participants:
        assert other_participant in remaining_participants
    assert participant_to_remove not in remaining_participants
