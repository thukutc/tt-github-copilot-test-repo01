"""
Integration tests for complete signup workflows.

Tests cover:
- End-to-end signup flow (fetch activities → select → signup)
- Multiple signups in sequence with proper state transitions
- Complex scenarios involving multiple activities and users
"""

import pytest


@pytest.mark.integration
def test_fetch_activities_then_signup_workflow(client, sample_emails):
    """
    Arrange: No setup needed
    Act: First fetch all activities, then sign up a student for one
    Assert: Verify activities fetched successfully and signup succeeds
    """
    # Arrange & Act: Fetch activities
    get_response = client.get("/activities")

    # Assert activities retrieved
    assert get_response.status_code == 200
    activities = get_response.json()
    assert "Chess Club" in activities

    # Act: Sign up for an activity from the list
    activity_name = "Chess Club"
    email = sample_emails["new"]
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert signup succeeded
    assert signup_response.status_code == 200
    assert email in signup_response.json()["message"]


@pytest.mark.integration
def test_signup_same_student_different_activities(client, sample_emails):
    """
    Arrange: Prepare one student and multiple activities
    Act: Sign up the same student for different activities sequentially
    Assert: Verify each signup succeeds and student appears in both activities
    """
    # Arrange
    student_email = sample_emails["new"]
    activities_to_join = ["Chess Club", "Programming Class", "Soccer Team"]

    # Act & Assert: Sign up for each activity
    for activity_name in activities_to_join:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        assert response.status_code == 200
        assert student_email in response.json()["message"]

    # Verify student is in all activities
    get_response = client.get("/activities")
    activities = get_response.json()
    for activity_name in activities_to_join:
        assert student_email in activities[activity_name]["participants"]


@pytest.mark.integration
def test_signup_multiple_students_same_activity(client, sample_emails):
    """
    Arrange: Prepare one activity and multiple student emails
    Act: Sign up each student for the same activity
    Assert: Verify all signups succeed and activity has all students
    """
    # Arrange
    activity_name = "Gym Class"
    student_emails = [
        "new1@mergington.edu",
        "new2@mergington.edu",
        "new3@mergington.edu",
    ]

    # Act: Sign up each student
    for email in student_emails:
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # Assert: Verify all students are in activity
    get_response = client.get("/activities")
    activity_data = get_response.json()[activity_name]
    for email in student_emails:
        assert email in activity_data["participants"]


@pytest.mark.integration
def test_error_recovery_workflow(client, sample_emails):
    """
    Arrange: Prepare scenarios with errors and recovery
    Act: Try invalid signup, then recover with valid signup
    Assert: Verify errors don't prevent subsequent valid operations
    """
    # Arrange
    activity_name = "Drama Club"
    invalid_email = sample_emails["existing"]["drama"]  # Already signed up
    valid_email = sample_emails["new"]

    # Act: Attempt invalid signup (already signed up)
    error_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": invalid_email}
    )

    # Assert: Error returned
    assert error_response.status_code == 400

    # Act: Attempt valid signup with different email
    valid_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": valid_email}
    )

    # Assert: Valid signup succeeds
    assert valid_response.status_code == 200
    assert valid_email in valid_response.json()["message"]


@pytest.mark.integration
def test_check_activity_full_status_before_and_after(client, sample_emails):
    """
    Arrange: Get an activity with low capacity and check initial state
    Act: Sign up until full, checking counts before each signup
    Assert: Verify activity transitions from available to full correctly
    """
    # Arrange
    activity_name = "Art Workshop"  # max 14, has 2 participants
    get_response = client.get("/activities")
    initial_count = len(get_response.json()[activity_name]["participants"])
    max_capacity = get_response.json()[activity_name]["max_participants"]

    # Act & Assert: Sign up until full
    remaining_slots = max_capacity - initial_count
    for i in range(remaining_slots):
        email = f"student{i}@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200

    # Act & Assert: Try to signup when full
    final_email = "finalstudent@mergington.edu"
    final_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": final_email}
    )
    assert final_response.status_code == 400
    assert "Activity is full" in final_response.json()["detail"]
