from app.models.machine import MachineStatus


def create_site(client, auth_headers):
    response = client.post(
        "/api/v1/sites",
        json={"name": "Nantes Plant", "city": "Nantes", "country": "France"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def create_machine(client, auth_headers, site_id: int):
    response = client.post(
        "/api/v1/machines",
        json={
            "site_id": site_id,
            "code": "NAN-PMP-01",
            "name": "Pump 01",
            "machine_type": "pump",
            "status": "idle",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


def test_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "admin123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_protected_route_requires_token(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_create_machine(client, auth_headers):
    site = create_site(client, auth_headers)
    machine = create_machine(client, auth_headers, site["id"])

    assert machine["code"] == "NAN-PMP-01"
    assert machine["status"] == MachineStatus.IDLE


def test_create_measurement(client, auth_headers):
    site = create_site(client, auth_headers)
    machine = create_machine(client, auth_headers, site["id"])

    response = client.post(
        "/api/v1/measurements",
        json={
            "machine_id": machine["id"],
            "temperature": 71,
            "vibration": 4.1,
            "power": 63,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["machine_id"] == machine["id"]


def test_threshold_creates_alert(client, auth_headers):
    site = create_site(client, auth_headers)
    machine = create_machine(client, auth_headers, site["id"])

    response = client.post(
        "/api/v1/measurements",
        json={
            "machine_id": machine["id"],
            "temperature": 99,
            "vibration": 8.7,
            "power": 100,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201

    alerts_response = client.get("/api/v1/alerts", headers=auth_headers)
    assert alerts_response.status_code == 200
    alerts = alerts_response.json()
    assert len(alerts) == 1
    assert alerts[0]["level"] == "critical"


def test_dashboard_summary(client, auth_headers):
    seed_response = client.post("/api/v1/demo/seed", headers=auth_headers)
    assert seed_response.status_code == 200

    response = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    body = response.json()

    assert response.status_code == 200
    assert body["sites_count"] >= 3
    assert body["machines_count"] >= 6
    assert "recent_measurements" in body
