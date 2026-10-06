def _register_and_headers(db_client, email="roadmapuser@example.com"):
    response = db_client.post("/api/auth/register", json={"email": email, "password": "supersecret123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _skill_gap_payload():
    return {
        "strong_skills": ["Python"],
        "develop_skills": ["SQL"],
        "missing_skills": ["Docker"],
        "priority_skills": ["Docker"],
        "scoring_note": "note",
    }


def _generate_payload():
    return {
        "target_career": "AI Engineer",
        "experience_level": "Beginner",
        "skill_gap": _skill_gap_payload(),
        "include_resources": False,
    }


def test_anonymous_generate_is_not_saved(db_client):
    response = db_client.post("/api/roadmap/generate", json=_generate_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["saved"] is False
    assert body["roadmap_id"] is None


def test_get_roadmap_without_any_saved_roadmap_is_404(db_client):
    headers = _register_and_headers(db_client)
    response = db_client.get("/api/roadmap", headers=headers)
    assert response.status_code == 404


def test_authenticated_generate_is_saved_and_retrievable(db_client):
    headers = _register_and_headers(db_client)

    generate_response = db_client.post("/api/roadmap/generate", headers=headers, json=_generate_payload())
    assert generate_response.status_code == 200
    gen_body = generate_response.json()
    assert gen_body["saved"] is True
    assert gen_body["roadmap_id"] is not None

    get_response = db_client.get("/api/roadmap", headers=headers)
    assert get_response.status_code == 200
    saved = get_response.json()
    assert saved["id"] == gen_body["roadmap_id"]
    assert saved["target_career"] == "AI Engineer"
    assert saved["roadmap"]["phases"] == gen_body["roadmap"]["phases"]


def test_get_roadmap_returns_most_recent(db_client):
    headers = _register_and_headers(db_client)

    payload1 = _generate_payload()
    payload1["target_career"] = "Backend Developer"
    db_client.post("/api/roadmap/generate", headers=headers, json=payload1)

    payload2 = _generate_payload()
    payload2["target_career"] = "AI Engineer"
    db_client.post("/api/roadmap/generate", headers=headers, json=payload2)

    response = db_client.get("/api/roadmap", headers=headers)
    assert response.json()["target_career"] == "AI Engineer"


def test_get_roadmap_requires_auth(db_client):
    response = db_client.get("/api/roadmap")
    assert response.status_code == 401


def test_roadmaps_are_isolated_per_user(db_client):
    headers_a = _register_and_headers(db_client, email="rma@example.com")
    headers_b = _register_and_headers(db_client, email="rmb@example.com")

    db_client.post("/api/roadmap/generate", headers=headers_a, json=_generate_payload())

    response_b = db_client.get("/api/roadmap", headers=headers_b)
    assert response_b.status_code == 404
