"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    # Save original state
    original_activities = {
        name: {**details, "participants": details["participants"].copy()}
        for name, details in activities.items()
    }
    
    yield
    
    # Restore original state
    for name in activities:
        activities[name]["participants"] = original_activities[name]["participants"].copy()


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    """Test successful signup for an activity"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    # Remove test email if it exists
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate(client):
    """Test that duplicate signup is rejected"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    # First signup
    activities[activity_name]["participants"].append(email)
    
    # Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_invalid_activity(client):
    """Test signup for non-existent activity"""
    email = "test@mergington.edu"
    activity_name = "NonExistent Activity"
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_participant_success(client):
    """Test successful deletion of a participant"""
    email = "test@mergington.edu"
    activity_name = "Chess Club"
    
    # Add participant first
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)
    
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert email not in activities[activity_name]["participants"]


def test_delete_participant_not_found(client):
    """Test deleting a participant that doesn't exist"""
    email = "nonexistent@mergington.edu"
    activity_name = "Chess Club"
    
    # Ensure participant is not in the list
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
    
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_delete_participant_invalid_activity(client):
    """Test deleting participant from non-existent activity"""
    email = "test@mergington.edu"
    activity_name = "NonExistent Activity"
    
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_multiple_signups_different_activities(client):
    """Test that a user can sign up for multiple activities"""
    email = "test@mergington.edu"
    
    # Remove from all activities first
    for activity in activities.values():
        if email in activity["participants"]:
            activity["participants"].remove(email)
    
    # Sign up for Chess Club
    response1 = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response1.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    
    # Sign up for Programming Class
    response2 = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response2.status_code == 200
    assert email in activities["Programming Class"]["participants"]


def test_activity_data_structure(client):
    """Test that activity data has the correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
        assert isinstance(activity_data["max_participants"], int)
