import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check structure of an activity
    activity = next(iter(activities.values()))
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test_student@mergington.edu"
    
    # First ensure the student isn't already signed up
    response = client.get("/activities")
    activities = response.json()
    if email in activities[activity_name]["participants"]:
        # Unregister first if already registered
        client.post(f"/activities/{activity_name}/unregister?email={email}")
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the student is now in the participants list
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using an email we know is registered
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_success():
    """Test successful unregistration from activity"""
    activity_name = "Chess Club"
    email = "test_unregister@mergington.edu"
    
    # First sign up the student
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify the student is no longer in the participants list
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who isn't registered"""
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()