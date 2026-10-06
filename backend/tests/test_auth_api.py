def test_register_creates_user_and_returns_token(db_client):
    response = db_client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "supersecret123", "full_name": "Alice"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "alice@example.com"
    assert "hashed_password" not in body["user"]
    assert "password" not in body["user"]


def test_register_duplicate_email_rejected(db_client):
    payload = {"email": "bob@example.com", "password": "supersecret123"}
    first = db_client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = db_client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_register_email_is_case_insensitive_for_duplicates(db_client):
    db_client.post("/api/auth/register", json={"email": "Carol@Example.com", "password": "supersecret123"})
    dup = db_client.post("/api/auth/register", json={"email": "carol@example.com", "password": "supersecret123"})
    assert dup.status_code == 409


def test_register_rejects_short_password(db_client):
    response = db_client.post("/api/auth/register", json={"email": "dave@example.com", "password": "short"})
    assert response.status_code == 422


def test_login_success(db_client):
    db_client.post("/api/auth/register", json={"email": "erin@example.com", "password": "supersecret123"})
    response = db_client.post("/api/auth/login", json={"email": "erin@example.com", "password": "supersecret123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password(db_client):
    db_client.post("/api/auth/register", json={"email": "frank@example.com", "password": "supersecret123"})
    response = db_client.post("/api/auth/login", json={"email": "frank@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_login_nonexistent_user(db_client):
    response = db_client.post("/api/auth/login", json={"email": "ghost@example.com", "password": "supersecret123"})
    assert response.status_code == 401


def test_me_requires_token(db_client):
    response = db_client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(db_client):
    register = db_client.post(
        "/api/auth/register", json={"email": "grace@example.com", "password": "supersecret123"}
    )
    token = register.json()["access_token"]
    response = db_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "grace@example.com"


def test_me_rejects_invalid_token(db_client):
    response = db_client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
