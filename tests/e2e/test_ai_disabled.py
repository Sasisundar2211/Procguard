def test_ai_disabled_still_blocks(client, sop, role_map, monkeypatch):
    monkeypatch.setenv("AI_ENABLED", "false")

    execution = [
        {"step_id": "1", "actor": "operator"},
        # Skip step 2
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
    assert body.get("explanation") is None
