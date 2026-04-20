import uuid


def create_asset(client, auth_headers):
    unique_suffix = uuid.uuid4().hex
    octet_3 = int(unique_suffix[:2], 16)
    octet_4 = int(unique_suffix[2:4], 16)

    response = client.post(
        "/assets/",
        json={
            "hostname": f"srv-{unique_suffix[:8]}",
            "ip_address": f"172.16.{octet_3}.{octet_4}",
            "owner": "network-team",
            "environment": "production",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    return response.json()


def create_incident(client, auth_headers, asset_id, severity="medium"):
    response = client.post(
        "/incidents/",
        json={
            "title": f"Incident {uuid.uuid4().hex[:8]}",
            "description": "Automatically generated test incident",
            "severity": severity,
            "asset_id": asset_id,
            "assigned_to": None,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    return response.json()


def test_stats_requires_auth(client):
    response = client.get("/stats/summary")
    assert response.status_code == 401


def test_stats_empty_summary(client, auth_headers):
    response = client.get("/stats/summary", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_incidents"] == 0
    assert data["open_incidents"] == 0
    assert data["in_progress_incidents"] == 0
    assert data["closed_incidents"] == 0
    assert data["critical_incidents"] == 0


def test_stats_summary_counts_incidents(client, auth_headers):
    asset = create_asset(client, auth_headers)

    incident_open = create_incident(
        client,
        auth_headers,
        asset["id"],
        severity="medium",
    )

    incident_in_progress = create_incident(
        client,
        auth_headers,
        asset["id"],
        severity="high",
    )

    incident_closed_critical = create_incident(
        client,
        auth_headers,
        asset["id"],
        severity="critical",
    )

    progress_response = client.patch(
        f"/incidents/{incident_in_progress['id']}",
        json={"status": "in_progress"},
        headers=auth_headers,
    )
    assert progress_response.status_code == 200

    closed_response = client.patch(
        f"/incidents/{incident_closed_critical['id']}",
        json={"status": "closed"},
        headers=auth_headers,
    )
    assert closed_response.status_code == 200

    response = client.get("/stats/summary", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_incidents"] == 3
    assert data["open_incidents"] == 1
    assert data["in_progress_incidents"] == 1
    assert data["closed_incidents"] == 1
    assert data["critical_incidents"] == 1

    assert incident_open["status"] == "open"