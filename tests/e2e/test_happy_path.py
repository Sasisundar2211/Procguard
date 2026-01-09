def test_happy_path(client, sop, role_map):
    execution = [
        {"step_id": "1", "actor": "operator"},
        {"step_id": "2", "actor": "operator"},
        {"step_id": "3", "actor": "supervisor"}
    ]

    response = client.post("/execute", json={
        "procedure": sop,
        "execution": execution,
        "roles": role_map
    })

    assert response.status_code == 200
    assert response.json()["violation"] is None
