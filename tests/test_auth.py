import uuid


def test_register_login_me(client):
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "StrongPass123"

    register_response = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["username"] == username
    assert register_data["email"] == email
    assert "password" not in register_data

    login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    token = login_data["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == username
    assert me_data["email"] == email


def test_register_duplicate_user_fails(client):
    payload = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "password": "StrongPass123",
    }

    first_response = client.post("/auth/register", json=payload)
    second_response = client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Username or email already exists"


def test_login_wrong_password_fails(client):
    payload = {
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "StrongPass123",
    }

    register_response = client.post("/auth/register", json=payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": payload["username"],
            "password": "BadPassword123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Incorrect username or password"