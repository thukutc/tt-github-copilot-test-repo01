"""
Unit tests for validation logic in the Mergington High School API.

Tests cover:
- Duplicate email detection
- Activity capacity constraints
- Activity existence validation
"""

import pytest


@pytest.mark.unit
def test_duplicate_email_rejected(client, sample_emails):
    """
    Arrange: Prepare a student email already signed up for Chess Club
    Act: Attempt to sign up the same email again
    Assert: Verify 400 status and appropriate error message
    """
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = sample_emails["existing"]["chess"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


@pytest.mark.unit
def test_activity_not_found_returns_404(client, sample_emails):
    """
    Arrange: Prepare a non-existent activity name
    Act: Attempt to sign up for the invalid activity
    Assert: Verify 404 status and appropriate error message
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


@pytest.mark.unit
def test_activity_at_capacity_rejected(client, sample_emails):
    """
    Arrange: Identify Math Olympiad (max 10, currently 2 participants)
             Fill it to capacity by adding 8 new students
    Act: Attempt to sign up one more student when at capacity
    Assert: Verify 400 status and appropriate error message
    """
    # Arrange
    activity_name = "Math Olympiad"
    # Math Olympiad has max 10 participants, currently has 2
    # We need to fill it up first
    fill_emails = [
        "fill1@mergington.edu",
        "fill2@mergington.edu",
        "fill3@mergington.edu",
        "fill4@mergington.edu",
        "fill5@mergington.edu",
        "fill6@mergington.edu",
        "fill7@mergington.edu",
        "fill8@mergington.edu",
    ]
    
    # Fill the activity to capacity
    for email in fill_emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # Act: Try to sign up one more when at capacity
    overflow_email = sample_emails["another"]
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": overflow_email}
    )

    # Assert
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]


@pytest.mark.unit
def test_successful_signup_returns_200_with_message(client, sample_emails):
    """
    Arrange: Prepare a valid activity and new email address
    Act: Call the signup endpoint with valid data
    Assert: Verify 200 status and correct message format
    """
    # Arrange
    activity_name = "Programming Class"
    new_email = sample_emails["new"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
