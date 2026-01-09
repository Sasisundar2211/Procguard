from fastapi.testclient import TestClient
from app.main import app
from app.core.fsm import State
import uuid

client = TestClient(app)

def test_api_full_flow():
    # 1. Create a Batch (as OPERATOR)
    batch_id = str(uuid.uuid4())
    procedure_id = "11111111-1111-1111-1111-111111111111"
    
    headers_operator = {
        "X-Actor-ID": "operator_1",
        "X-Actor-Role": "OPERATOR"
    }
    
    response = client.post(
        "/batches/",
        json={
            "batch_id": batch_id,
            "procedure_id": procedure_id,
            "procedure_version": 1
        },
        headers=headers_operator
    )
    print(response.json())
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    assert response.json()["current_state"] == "IN_PROGRESS"
    
    # 2. Progress Step (as OPERATOR)
    response = client.post(
        f"/batches/{batch_id}/event",
        json={
            "event": "progress_step", # Changed from event_type
            # "payload": ... Forbidden in new schema
            "step_id": "step-1" # Optional example
        },
        headers=headers_operator
    )
    print("Step 2 Response:", response.status_code, response.text)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["current_state"] == "COMPLETED"

    # 3. Try Unauthorized Action (as AUDITOR)
    # create fresh batch first to ensure valid FSM state
    batch_id_2 = str(uuid.uuid4())
    client.post( "/batches/", json={"batch_id": batch_id_2, "procedure_id": procedure_id, "procedure_version": 1}, headers=headers_operator)

    headers_auditor = {
        "X-Actor-ID": "auditor_1",
        "X-Actor-Role": "AUDITOR"
    }
    response = client.post(
        f"/batches/{batch_id_2}/event",
        json={"event": "reject_batch"}, # Changed from event_type
        headers=headers_auditor
    )
    # Should be 403 Forbidden
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"

    print("API Integration Test Passed!")

if __name__ == "__main__":
    test_api_full_flow()
