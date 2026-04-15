import uuid


def create_asset(client, auth_headers):
    unique_suffix = uuid.uuid4().hex
    octet_3 = int(unique_suffix[:2], 16)
    octet_4 = int(unique_suffix[2:4], 16)

    response = client.post(
        "/assets/",
        json={
            "hostname": f"srv-{unique_suffix[:8]}",
            "ip_address": f"10.0.{octet_3}.{octet_4}",
            "owner": "network-team",
            "environment": "production",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def create_incident(client, auth_headers, asset_id, severity="high"):
    response = client.post(
        "/incidents/",
        json={
            "title": "High CPU usage on server",
            "description": "CPU usage exceeded threshold",
            "severity": severity,
            "asset_id": asset_id,
            "assigned_to": None,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def test_incidents_requires_auth(client):
    response = client.get("/incidents/")
    assert response.status_code == 401


def test_create_incident_fails_without_existing_asset(client, auth_headers):
    response = client.post(
        "/incidents/",
        json={
            "title": "Server down",
            "description": "Server is not responding",
            "severity": "critical",
            "asset_id": 999,
            "assigned_to": None,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"


def test_create_list_and_get_incident(client, auth_headers):
    asset = create_asset(client, auth_headers)

    create_response = client.post(
        "/incidents/",
        json={
            "title": "Disk almost full",
            "description": "Disk usage exceeded 90 percent",
            "severity": "medium",
            "asset_id": asset["id"],
            "assigned_to": None,
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    incident = create_response.json()
    assert incident["title"] == "Disk almost full"
    assert incident["asset_id"] == asset["id"]
    assert incident["status"] == "open"

    list_response = client.get("/incidents/", headers=auth_headers)
    assert list_response.status_code == 200
    incidents = list_response.json()
    assert len(incidents) == 1
    assert incidents[0]["title"] == "Disk almost full"

    get_response = client.get(f"/incidents/{incident['id']}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == incident["id"]


def test_update_and_delete_incident(client, auth_headers):
    asset = create_asset(client, auth_headers)
    incident = create_incident(client, auth_headers, asset["id"], severity="high")

    update_response = client.patch(
        f"/incidents/{incident['id']}",
        json={
            "status": "closed",
            "severity": "critical",
            "description": "Issue resolved after restart",
        },
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["status"] == "closed"
    assert updated["severity"] == "critical"
    assert updated["description"] == "Issue resolved after restart"

    delete_response = client.delete(f"/incidents/{incident['id']}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Incident deleted"

    get_deleted_response = client.get(f"/incidents/{incident['id']}", headers=auth_headers)
    assert get_deleted_response.status_code == 404


def test_incident_filters(client, auth_headers):
    asset_1 = create_asset(client, auth_headers)
    asset_2 = create_asset(client, auth_headers)

    incident_1 = create_incident(client, auth_headers, asset_1["id"], severity="high")
    incident_2 = create_incident(client, auth_headers, asset_2["id"], severity="critical")

    client.patch(
        f"/incidents/{incident_1['id']}",
        json={"status": "in_progress"},
        headers=auth_headers,
    )

    client.patch(
        f"/incidents/{incident_2['id']}",
        json={"status": "closed"},
        headers=auth_headers,
    )

    by_severity = client.get("/incidents/?severity=critical", headers=auth_headers)
    assert by_severity.status_code == 200
    severity_data = by_severity.json()
    assert len(severity_data) == 1
    assert severity_data[0]["severity"] == "critical"

    by_status = client.get("/incidents/?status=in_progress", headers=auth_headers)
    assert by_status.status_code == 200
    status_data = by_status.json()
    assert len(status_data) == 1
    assert status_data[0]["status"] == "in_progress"

    by_asset = client.get(f"/incidents/?asset_id={asset_1['id']}", headers=auth_headers)
    assert by_asset.status_code == 200
    asset_data = by_asset.json()
    assert len(asset_data) == 1
    assert asset_data[0]["asset_id"] == asset_1["id"]