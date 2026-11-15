"""Automated tests for Conversation and Query Orchestration endpoints."""


def test_create_and_list_conversations(client, user_token):
    # Create conversation
    create_resp = client.post(
        "/api/v1/conversations",
        json={"title": "Consumer Laptop Issue", "legal_domain": "consumer"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert create_resp.status_code == 201
    conv_id = create_resp.json()["id"]

    # List conversations
    list_resp = client.get(
        "/api/v1/conversations",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert list_resp.status_code == 200
    convs = list_resp.json()
    assert any(c["id"] == conv_id for c in convs)


def test_submit_query_orchestration_and_safety_disclaimer(client, user_token):
    # Create conversation
    create_resp = client.post(
        "/api/v1/conversations",
        json={"title": "Defective Goods Inquiry"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    conv_id = create_resp.json()["id"]

    # Submit legal query
    query_resp = client.post(
        f"/api/v1/conversations/{conv_id}/query",
        json={"question": "The seller refused to fix a defective laptop under warranty. What can I do?"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert query_resp.status_code == 200
    data = query_resp.json()
    assert data["status"] == "answered"
    assert data["legal_domain"] == "consumer"
    assert len(data["citations"]) >= 1
    assert "DISCLAIMER" in data["disclaimer"]
    assert len(data["procedural_steps"]) >= 1


def test_user_data_isolation_forbidden_cross_access(client, admin_token, user_token):
    # Create conversation as user (id: 3)
    create_resp = client.post(
        "/api/v1/conversations",
        json={"title": "Private User Query"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    conv_id = create_resp.json()["id"]

    # Try accessing as admin (id: 1) without ownership -> Should be 403 Forbidden (REQ-HIST-04)
    access_resp = client.get(
        f"/api/v1/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert access_resp.status_code == 403
