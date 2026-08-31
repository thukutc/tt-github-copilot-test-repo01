"""
Shared test configuration and fixtures for the Mergington High School API tests.

Provides:
- app: FastAPI application instance for testing
- client: TestClient for making HTTP requests to the app with fresh state
- sample_activities: Copy of the activities database for test isolation
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient

from src.app import app, activities


# Store the initial activities state for reset between tests
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the FastAPI app.
    
    Resets the app's activities to initial state before each test to ensure
    test isolation and prevent cross-test state pollution.
    
    Returns:
        TestClient: A test client configured for the FastAPI app with fresh state
    """
    # Reset activities to initial state before each test
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Provide an isolated copy of the activities database for tests.
    
    Each test gets a fresh copy to prevent cross-test state pollution.
    
    Returns:
        dict: Deep copy of the activities database
    """
    return deepcopy(activities)


@pytest.fixture
def sample_emails():
    """
    Provide a collection of test email addresses.
    
    Returns:
        dict: Email addresses for various test scenarios
    """
    return {
        "existing": {
            "chess": "michael@mergington.edu",
            "programming": "emma@mergington.edu",
            "gym": "john@mergington.edu",
            "soccer": "alex@mergington.edu",
            "basketball": "noah@mergington.edu",
            "drama": "lily@mergington.edu",
            "art": "ava@mergington.edu",
            "math": "liam@mergington.edu",
            "science": "charlotte@mergington.edu",
        },
        "new": "newstudent@mergington.edu",
        "another": "anotherstudent@mergington.edu",
        "test_user": "testuser@mergington.edu",
    }
