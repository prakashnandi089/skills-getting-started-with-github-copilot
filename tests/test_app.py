import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

def test_signup_valid_email():
    response = client.post("/activities/Chess Club/signup?email=testuser@mergington.edu")
    assert response.status_code == 200
    assert "Signed up testuser@mergington.edu for Chess Club" in response.json()["message"]

def test_signup_invalid_email():
    response = client.post("/activities/Chess Club/signup?email=invalid-email")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email address"

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_participant():
    # First, sign up a user
    email = "deleteuser@mergington.edu"
    client.post(f"/activities/Gym Class/signup?email={email}")
    # Now, unregister
    response = client.delete(f"/activities/Gym Class/unregister?email={email}")
    assert response.status_code == 200
    assert f"Unregistered {email} from Gym Class" in response.json()["message"]

def test_unregister_not_registered():
    response = client.delete("/activities/Gym Class/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
