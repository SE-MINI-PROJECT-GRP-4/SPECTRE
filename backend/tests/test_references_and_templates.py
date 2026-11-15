"""Automated tests for Legal References and Document Templates."""


def test_list_and_search_legal_references(client):
    response = client.get("/api/v1/references?domain=consumer")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Consumer Protection" in item["title"] for item in data["items"])


def test_list_and_render_document_template(client):
    # List templates
    list_resp = client.get("/api/v1/templates")
    assert list_resp.status_code == 200
    templates = list_resp.json()
    assert len(templates) >= 1

    # Pick consumer template
    tpl = next((t for t in templates if t["slug"] == "consumer-legal-notice"), templates[0])

    # Render template with variables
    render_resp = client.post(
        f"/api/v1/templates/{tpl['id']}/render",
        json={
            "variables": {
                "complainant_name": "Test Citizen",
                "opposite_party_name": "ABC Electronics",
                "purchase_date": "2026-10-01",
                "invoice_number": "INV-1002",
                "amount_paid": "50,000",
                "defect_description": "Motherboard failed",
                "demand_summary": "Immediate refund",
            }
        },
    )
    assert render_resp.status_code == 200
    rendered_data = render_resp.json()
    assert "Test Citizen" in rendered_data["rendered_document"]
    assert "DISCLAIMER" in rendered_data["rendered_document"]
