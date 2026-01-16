from datetime import datetime


def auth_headers():
    return {"Authorization": "Bearer test-token"}


def test_rpc_sync_partner(client):
    payload = {
        "jsonrpc": "2.0",
        "method": "partner.sync",
        "params": {
            "external_id": "ext-3001",
            "name": "Cliente RPC",
            "score": 0.88,
            "updated_at": datetime.utcnow().isoformat(),
        },
        "id": 1,
    }
    response = client.post("/rpc", json=payload, headers=auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["result"]["external_id"] == "ext-3001"
