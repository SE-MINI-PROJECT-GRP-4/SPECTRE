"""Automated tests for Administrative Management and Auditing endpoints."""


def test_admin_overview_requires_admin_role(client, user_token):
    # Standard user attempting admin endpoint -> 403 Forbidden (REQ-AUTH-06)
    response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_admin_overview_metrics_success(client, admin_token):
    response = client.get(
        "/api/v1/admin/overview",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] >= 1
    assert data["total_references"] >= 1
    assert data["total_templates"] >= 1


def test_admin_update_user_role_creates_audit_log(client, admin_token):
    # Update role for user 3 (citizen)
    response = client.put(
        "/api/v1/admin/users/3/role",
        json={"role": "advocate"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "advocate"

    # Verify audit log was recorded (REQ-ADMIN-06)
    audit_resp = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert any(log["action"] == "UPDATE_USER_ROLE" for log in logs)
