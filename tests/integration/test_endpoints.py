"""
Integration tests for the Mergington High School API endpoints.

Tests cover:
- GET /activities endpoint
- GET / root endpoint redirect
- POST /activities/{activity_name}/signup endpoint with various scenarios
"""

import pytest


@pytest.mark.integration
def test_get_activities_returns_all_activities(client):
    """
    Arrange: Prepare to call the GET /activities endpoint
    Act: Make a GET request to /activities
    Assert: Verify 200 status and response contains all activity names
    """
    # Arrange
    expected_activities = [
        "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
        "Basketball Club", "Drama Club", "Art Workshop", "Math Olympiad",
        "Science Club"
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert set(activities.keys()) == set(expected_activities)


@pytest.mark.integration
def test_get_activities_response_structure(client):
    """
    Arrange: Prepare to call the GET /activities endpoint
    Act: Make a GET request to /activities
    Assert: Verify response structure matches expected schema
    """
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_data, dict)
        assert required_fields.issubset(set(activity_data.keys()))
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)


@pytest.mark.integration
def test_root_redirects_to_index(client):
    """
    Arrange: Prepare to call the GET / endpoint
    Act: Make a GET request to / (follow_redirects=False to check redirect)
    Assert: Verify it redirects to /static/index.html
    """
    # Arrange & Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


@pytest.mark.integration
def test_successful_signup_adds_participant(client, sample_emails):
    """
    Arrange: Prepare activity name and new email address
    Act: Call POST /activities/{name}/signup with valid data
    Assert: Verify 200 status, correct message, and participant is added in response
    """
    # Arrange
    activity_name = "Chess Club"
    new_email = sample_emails["new"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert new_email in data["message"]
    assert activity_name in data["message"]


@pytest.mark.integration
def test_signup_duplicate_email_returns_400(client, sample_emails):
    """
    Arrange: Get an email already signed up for an activity
    Act: Attempt to sign up the same email for the same activity
    Assert: Verify 400 status and appropriate error detail
    """
    # Arrange
    activity_name = "Chess Club"
    existing_email = sample_emails["existing"]["chess"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


@pytest.mark.integration
def test_signup_invalid_activity_returns_404(client, sample_emails):
    """
    Arrange: Prepare invalid activity name and new email
    Act: Call POST with non-existent activity
    Assert: Verify 404 status and appropriate error detail
    """
    # Arrange
    invalid_activity = "Nonexistent Activity"
    email = sample_emails["new"]

    # Act
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


@pytest.mark.integration
def test_signup_at_capacity_returns_400(client, sample_emails):
    """
    Arrange: Select Math Olympiad (max 10, has 2), fill to capacity
    Act: Attempt to add one more participant
    Assert: Verify 400 status and "Activity is full" error message
    """
    # Arrange
    activity_name = "Math Olympiad"
    fill_emails = [
        "filler1@mergington.edu",
        "filler2@mergington.edu",
        "filler3@mergington.edu",
        "filler4@mergington.edu",
        "filler5@mergington.edu",
        "filler6@mergington.edu",
        "filler7@mergington.edu",
        "filler8@mergington.edu",
    ]

    # Fill activity to capacity
    for email in fill_emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # Act: Attempt signup when at capacity
    overflow_email = sample_emails["another"]
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": overflow_email}
    )

    # Assert
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]


@pytest.mark.integration
def test_multiple_signups_for_same_activity(client, sample_emails):
    """
    Arrange: Prepare multiple different emails for the same activity
    Act: Sign up each email sequentially
    Assert: Verify each signup succeeds with 200 status
    """
    # Arrange
    activity_name = "Programming Class"
    new_emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
    ]

    # Act & Assert
    for email in new_emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email in response.json()["message"]
