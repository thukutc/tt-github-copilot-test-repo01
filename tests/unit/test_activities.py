"""
Unit tests for activity data structure and properties.

Tests cover:
- Activity data structure and required fields
- Participant list operations
- Max participants boundary conditions
"""

import pytest


@pytest.mark.unit
def test_all_activities_have_required_fields(sample_activities):
    """
    Arrange: Get the sample activities database
    Act: Iterate through all activities and check for required fields
    Assert: Verify each activity has description, schedule, max_participants, and participants
    """
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act & Assert
    for activity_name, activity_data in sample_activities.items():
        assert isinstance(activity_data, dict), f"{activity_name} should be a dict"
        activity_fields = set(activity_data.keys())
        assert required_fields.issubset(activity_fields), \
            f"{activity_name} missing fields: {required_fields - activity_fields}"


@pytest.mark.unit
def test_participants_list_is_list_of_strings(sample_activities):
    """
    Arrange: Get the sample activities database
    Act: Check participants field type and contents
    Assert: Verify participants is a list containing only email strings
    """
    # Arrange & Act & Assert
    for activity_name, activity_data in sample_activities.items():
        participants = activity_data["participants"]
        assert isinstance(participants, list), \
            f"{activity_name} participants should be a list"
        for participant in participants:
            assert isinstance(participant, str), \
                f"{activity_name} participant {participant} should be a string"


@pytest.mark.unit
def test_max_participants_is_positive_integer(sample_activities):
    """
    Arrange: Get the sample activities database
    Act: Check max_participants field type and value
    Assert: Verify max_participants is a positive integer
    """
    # Arrange & Act & Assert
    for activity_name, activity_data in sample_activities.items():
        max_participants = activity_data["max_participants"]
        assert isinstance(max_participants, int), \
            f"{activity_name} max_participants should be an integer"
        assert max_participants > 0, \
            f"{activity_name} max_participants should be positive"


@pytest.mark.unit
def test_no_activity_exceeds_max_participants(sample_activities):
    """
    Arrange: Get the sample activities database
    Act: Check if current participants exceed max_participants
    Assert: Verify all activities have participants <= max_participants
    """
    # Arrange & Act & Assert
    for activity_name, activity_data in sample_activities.items():
        num_participants = len(activity_data["participants"])
        max_participants = activity_data["max_participants"]
        assert num_participants <= max_participants, \
            f"{activity_name} has {num_participants} participants but max is {max_participants}"


@pytest.mark.unit
def test_activity_names_are_string_keys(sample_activities):
    """
    Arrange: Get the sample activities database
    Act: Check activity name (dictionary key) types
    Assert: Verify all activity names are strings
    """
    # Arrange & Act & Assert
    for activity_name in sample_activities.keys():
        assert isinstance(activity_name, str), \
            f"Activity name {activity_name} should be a string"
        assert len(activity_name) > 0, \
            "Activity names should not be empty strings"
