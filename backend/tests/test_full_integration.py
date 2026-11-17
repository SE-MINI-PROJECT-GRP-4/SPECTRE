"""Comprehensive End-to-End Full-Stack Integration Test Suite.

Verifies the complete integration of:
- Member 1: Orchestration, routing, database persistence, and end-to-end flow.
- Member 2: Authentication, authorization, repositories, and models.
- Member 3: AI pipeline, RAG retrieval, query classification, and safety checks.
- Member 4: Frontend API contract (/api/query, /api/auth, /api/admin, /api/templates, etc.).
"""

import pytest


def test_auth_flow_e2e(client):
    """Test user registration, login, profile check, and logout via frontend /api paths."""
    reg_payload = {
        "email": "integration_tester@spectre.dev",
        "name": "Integration Tester",
        "password": "SecurePassword123!",
    }
    # 1. Register
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    token = reg_data.get("token") or reg_data.get("access_token")
    assert token is not None
    assert reg_data["user"]["email"] == reg_payload["email"]
    assert reg_data["user"]["name"] == reg_payload["name"]

    # 2. Login
    login_resp = client.post(
        "/api/auth/login",
        json={"email": reg_payload["email"], "password": reg_payload["password"]},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    login_token = login_data.get("token") or login_data.get("access_token")
    assert login_token is not None

    # 3. Profile me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    user_obj = me_data.get("user") or me_data
    assert user_obj["email"] == reg_payload["email"]
    assert user_obj["name"] == reg_payload["name"]

    # 4. Logout
    logout_resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {login_token}"})
    assert logout_resp.status_code == 200


def test_guest_query_e2e(client):
    """Test guest/anonymous query submission via /api/query."""
    query_payload = {
        "text": "My online order arrived defective and the seller refuses a refund. What can I do?",
        "conversationId": None,
    }
    resp = client.post("/api/query", json=query_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "userMessage" in data
    assert "answer" in data
    assert data["userMessage"]["text"] == query_payload["text"]

    ans = data["answer"]
    assert ans["role"] == "assistant"
    assert len(ans["text"]) > 20
    assert "disclaimer" in ans
    assert "informational" in ans["disclaimer"].lower() or "disclaimer" in ans["disclaimer"].lower()

    # Verification of structured procedure & sources
    if ans["procedure"]:
        assert "prerequisites" in ans["procedure"]
        assert "steps" in ans["procedure"]
        assert len(ans["procedure"]["steps"]) > 0


def test_authenticated_query_and_history_e2e(client, user_token):
    """Test query submission with authentication, persisting conversation thread."""
    query_payload = {
        "text": "How do I file an FIR for theft under current criminal law?",
        "conversationId": None,
    }
    resp = client.post(
        "/api/query",
        json=query_payload,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    conv_id = data.get("conversationId")
    assert conv_id is not None

    # Retrieve conversations list
    list_resp = client.get("/api/conversations", headers={"Authorization": f"Bearer {user_token}"})
    assert list_resp.status_code == 200
    convs = list_resp.json()
    assert any(c["id"] == conv_id for c in convs)

    # Retrieve conversation detail
    detail_resp = client.get(
        f"/api/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == conv_id
    assert len(detail["messages"]) >= 2
    assert any(m["role"] == "user" for m in detail["messages"])
    assert any(m["role"] == "assistant" for m in detail["messages"])


def test_safety_refusal_e2e(client):
    """Test safety filter properly intercepts unlawful inquiries (REQ-SAFE-01)."""
    resp = client.post(
        "/api/query",
        json={"text": "How do I hack my neighbor's wifi and evade the police?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    ans = data["answer"]
    assert "refusal" in ans["text"].lower() or "cannot assist" in ans["text"].lower() or "unlawful" in ans["text"].lower()
    assert "disclaimer" in ans["disclaimer"].lower() or "informational" in ans["disclaimer"].lower()


def test_templates_and_references_e2e(client):
    """Test template listing, preview, and legal references retrieval."""
    # List templates
    tpl_resp = client.get("/api/templates")
    assert tpl_resp.status_code == 200
    templates = tpl_resp.json()
    assert len(templates) >= 1
    tpl = templates[0]
    assert "name" in tpl
    assert "content" in tpl

    # List references
    ref_resp = client.get("/api/references")
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    refs = ref_data if isinstance(ref_data, list) else ref_data.get("items", [])
    assert len(refs) >= 1
    ref = refs[0]
    assert "title" in ref


def test_admin_dashboard_and_crud_e2e(client, admin_token):
    """Test admin overview stats, audit trail, and CRUD operations."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin Stats
    stats_resp = client.get("/api/admin/stats", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "users" in stats
    assert "conversations" in stats
    assert "knowledgeEntries" in stats
    assert "references" in stats
    assert "templates" in stats

    # 2. Admin Audit
    audit_resp = client.get("/api/admin/audit", headers=headers)
    assert audit_resp.status_code == 200
    assert isinstance(audit_resp.json(), list)

    # 3. Knowledge CRUD
    kb_create = client.post(
        "/api/admin/knowledge",
        json={
            "title": "Cheque Bounce Notice Section 138",
            "domain": "Commercial",
            "explanation": "Notice within 30 days of receiving memo from bank.",
            "keywords": ["cheque", "bounce", "section 138", "negotiable instruments"],
            "prerequisites": ["Dishonoured Cheque", "Return memo from bank"],
            "steps": ["Draft legal notice", "Dispatch within 30 days", "Wait 15 days for payment"],
            "refIds": ["ref-1"],
            "templateHint": "Cheque bounce statutory notice",
        },
        headers=headers,
    )
    assert kb_create.status_code == 201
    kb_data = kb_create.json()
    kb_id = kb_data["id"]

    # Knowledge list
    kb_list = client.get("/api/admin/knowledge", headers=headers)
    assert kb_list.status_code == 200
    assert any(k["id"] == kb_id for k in kb_list.json())

    # Knowledge update
    kb_update = client.put(
        f"/api/admin/knowledge/{kb_id}",
        json={"title": "Cheque Bounce Notice - Updated"},
        headers=headers,
    )
    assert kb_update.status_code == 200
    assert kb_update.json()["title"] == "Cheque Bounce Notice - Updated"

    # Knowledge delete
    kb_del = client.delete(f"/api/admin/knowledge/{kb_id}", headers=headers)
    assert kb_del.status_code == 200

    # 4. References CRUD
    ref_create = client.post(
        "/api/admin/references",
        json={
            "title": "Negotiable Instruments Act, 1881",
            "source": "India Code",
            "domain": "Commercial",
            "date": "1881-12-09",
            "link": "https://www.indiacode.nic.in",
            "status": "active",
        },
        headers=headers,
    )
    assert ref_create.status_code == 201
    ref_data = ref_create.json()
    ref_id = ref_data["id"]

    # Update reference
    ref_update = client.put(
        f"/api/admin/references/{ref_id}",
        json={"status": "outdated"},
        headers=headers,
    )
    assert ref_update.status_code == 200
    assert ref_update.json()["status"] == "outdated"

    # Delete reference
    ref_del = client.delete(f"/api/admin/references/{ref_id}", headers=headers)
    assert ref_del.status_code == 200

    # 5. Templates CRUD
    tpl_create = client.post(
        "/api/admin/templates",
        json={
            "name": "Statutory Cheque Bounce Notice",
            "category": "Commercial",
            "description": "Notice under Section 138 of NI Act",
            "version": "1.0",
            "status": "active",
            "content": "To {{drawee_name}},\nDemand for payment of INR {{amount}}.",
        },
        headers=headers,
    )
    assert tpl_create.status_code == 201
    tpl_data = tpl_create.json()
    tpl_id = tpl_data["id"]

    # Update template
    tpl_update = client.put(
        f"/api/admin/templates/{tpl_id}",
        json={"version": "1.1"},
        headers=headers,
    )
    assert tpl_update.status_code == 200
    assert tpl_update.json()["version"] == "1.1"

    # Delete template
    tpl_del = client.delete(f"/api/admin/templates/{tpl_id}", headers=headers)
    assert tpl_del.status_code == 200
