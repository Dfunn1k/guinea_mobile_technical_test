from datetime import datetime, timedelta


def auth_headers():
    return {"Authorization": "Bearer test-token"}


def test_create_partner_idempotent(client):
    payload = {
        "external_id": "ext-2001",
        "name": "Cliente Uno",
        "email": "uno@example.com",
        "score": 0.5,
        "updated_at": datetime.utcnow().isoformat(),
    }
    response = client.post("/partners", json=payload, headers=auth_headers())
    assert response.status_code == 200

    response_repeat = client.post("/partners", json=payload, headers=auth_headers())
    assert response_repeat.status_code == 200
    assert response_repeat.json()["external_id"] == "ext-2001"


def test_conflict_when_older_update(client):
    now = datetime.utcnow()
    payload = {
        "external_id": "ext-2002",
        "name": "Cliente Dos",
        "updated_at": now.isoformat(),
    }
    response = client.post("/partners", json=payload, headers=auth_headers())
    assert response.status_code == 200

    older_payload = {
        "external_id": "ext-2002",
        "name": "Cliente Dos Viejo",
        "updated_at": (now - timedelta(days=1)).isoformat(),
    }
    conflict = client.post("/partners", json=older_payload, headers=auth_headers())
    assert conflict.status_code == 409
