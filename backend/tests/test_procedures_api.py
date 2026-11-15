"""Automated tests for Legal Procedure Guidance endpoints."""


def test_list_procedures(client):
    response = client.get("/api/v1/procedures")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_get_procedure_by_slug(client):
    response = client.get("/api/v1/procedures/fir-registration-bnss")
    assert response.status_code == 200
    data = response.json()
    assert "FIR" in data["title"]
    assert len(data["steps"]) >= 4
    assert len(data["prerequisites"]) >= 1
    assert "DISCLAIMER" in data["disclaimer"]
