import copy

import pytest
from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)
DEFAULT_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(DEFAULT_ACTIVITIES))


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in response.json()["message"]

    updated = client.get("/activities").json()
    assert email in updated["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "repeat@mergington.edu"
    client.post("/activities/Chess%20Club/signup", params={"email": email})
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_existing_participant():
    participant = "michael@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": participant},
    )

    assert response.status_code == 200
    assert participant in response.json()["message"]

    updated = client.get("/activities").json()
    assert participant not in updated["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
