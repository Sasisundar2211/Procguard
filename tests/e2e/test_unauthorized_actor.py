def test_unauthorized_actor(client, sop, role_map):
    execution = [
        {"step_id": "1", "actor": "operator"},
        {"step_id": "2", "actor": "operator"},
        {"step_id": "3", "actor": "operator"} # Operator trying to approve
    ]

    response = client.post("/execute", json={
        "procedure": sop,
        "execution": execution,
        "roles": role_map
    })

    body = response.json()

    assert response.status_code == 403
    assert body["violation"]["code"] == "UNAUTHORIZED_ACTOR"
