"""Automated tests for Authentication and Authorization endpoints."""


def test_register_new_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_register_duplicate_email_conflict(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "citizen@spectre.legal",  # already seeded
            "password": "Password123!",
            "full_name": "Duplicate User",
        },
    )
    assert response.status_code == 409


def test_login_success_and_jwt_issuance(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "citizen@spectre.legal",
            "password": "User@SPECTRE2026!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "citizen@spectre.legal"


def test_login_invalid_password_unauthorized(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "citizen@spectre.legal",
            "password": "WrongPassword999!",
        },
    )
    assert response.status_code == 401


def test_get_current_user_profile(client, user_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "citizen@spectre.legal"
