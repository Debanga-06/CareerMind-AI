def _register_and_headers(db_client, email="profile@example.com"):
    response = db_client.post("/api/auth/register", json={"email": email, "password": "supersecret123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_requires_auth(db_client):
    response = db_client.get("/api/profile")
    assert response.status_code == 401


def test_get_profile_defaults_when_unset(db_client):
    headers = _register_and_headers(db_client)
    response = db_client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["skills"] == []
    assert body["target_career"] is None


def test_put_profile_creates_and_persists(db_client):
    headers = _register_and_headers(db_client)
    response = db_client.put(
        "/api/profile",
        headers=headers,
        json={
            "target_career": "AI Engineer",
            "experience_level": "Beginner",
            "location": "India",
            "skills": ["Python", "Git"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["target_career"] == "AI Engineer"
    assert body["skills"] == ["Python", "Git"]
    assert body["updated_at"] is not None

    # Persisted -> GET reflects the same data.
    follow_up = db_client.get("/api/profile", headers=headers)
    assert follow_up.json()["target_career"] == "AI Engineer"


def test_put_profile_partial_update_preserves_other_fields(db_client):
    headers = _register_and_headers(db_client)
    db_client.put(
        "/api/profile",
        headers=headers,
        json={"target_career": "Data Scientist", "skills": ["SQL"]},
    )
    response = db_client.put("/api/profile", headers=headers, json={"location": "Remote"})
    assert response.status_code == 200
    body = response.json()
    assert body["target_career"] == "Data Scientist"  # preserved
    assert body["skills"] == ["SQL"]  # preserved
    assert body["location"] == "Remote"  # updated


def test_profiles_are_isolated_per_user(db_client):
    headers_a = _register_and_headers(db_client, email="usera@example.com")
    headers_b = _register_and_headers(db_client, email="userb@example.com")

    db_client.put("/api/profile", headers=headers_a, json={"target_career": "Backend Developer"})

    profile_b = db_client.get("/api/profile", headers=headers_b)
    assert profile_b.json()["target_career"] is None
