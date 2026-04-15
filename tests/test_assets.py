import uuid


def test_assets_requires_auth(client):
    response = client.get("/assets/")
    assert response.status_code == 401


def test_create_and_list_assets(client, auth_headers):
    create_response = client.post(
        "/assets/",
        json={
            "hostname": "srv-web-01",
            "ip_address": "192.168.1.10",
            "owner": "network-team",
            "environment": "production",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created_asset = create_response.json()
    assert created_asset["hostname"] == "srv-web-01"

    list_response = client.get("/assets/", headers=auth_headers)
    assert list_response.status_code == 200
    assets = list_response.json()
    assert len(assets) == 1
    assert assets[0]["hostname"] == "srv-web-01"


def test_duplicate_asset_fails(client, auth_headers):
    unique_suffix = uuid.uuid4().hex[:8]

    payload = {
        "hostname": f"srv-web-{unique_suffix}",
        "ip_address": f"192.168.1.{int(unique_suffix[:2], 16) % 200 + 1}",
        "owner": "network-team",
        "environment": "production",
    }

    first_response = client.post("/assets/", json=payload, headers=auth_headers)
    second_response = client.post("/assets/", json=payload, headers=auth_headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Hostname or IP already exists"


def test_get_update_delete_asset(client, auth_headers):
    create_response = client.post(
        "/assets/",
        json={
            "hostname": "srv-db-01",
            "ip_address": "192.168.1.20",
            "owner": "database-team",
            "environment": "staging",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    asset_id = create_response.json()["id"]

    get_response = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["hostname"] == "srv-db-01"

    update_response = client.patch(
        f"/assets/{asset_id}",
        json={
            "owner": "infra-team",
            "environment": "production",
        },
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    updated_asset = update_response.json()
    assert updated_asset["owner"] == "infra-team"
    assert updated_asset["environment"] == "production"

    delete_response = client.delete(f"/assets/{asset_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Asset deleted"

    get_deleted_response = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert get_deleted_response.status_code == 404