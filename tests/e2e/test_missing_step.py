def test_missing_step(client, sop, role_map):
    execution = [
        {"step_id": "1", "actor": "operator"},
        {"step_id": "3", "actor": "supervisor"}
    ]

    response = client.post("/execute", json={
        "procedure": sop,
        "execution": execution,
        "roles": role_map
    })

    body = response.json()

    assert response.status_code == 403
    assert body["violation"]["code"] == "MISSING_REQUIRED_STEP"
