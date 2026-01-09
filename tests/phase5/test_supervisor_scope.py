from fastapi.testclient import TestClient
from app.main import app
import uuid
import pytest

client = TestClient(app)

@pytest.fixture
def clean_batch():
    batch_id = str(uuid.uuid4())
    procedure_id = "11111111-1111-1111-1111-111111111111"
    
    headers_operator = {
        "X-Actor-ID": "operator_1",
        "X-Actor-Role": "OPERATOR"
    }
    
    # Create batch as OPERATOR
    response = client.post(
        "/batches/",
        json={
            "batch_id": batch_id,
            "procedure_id": procedure_id,
            "procedure_version": 1
        },
        headers=headers_operator
    )
    assert response.status_code == 201
    return batch_id

def test_supervisor_cannot_progress(clean_batch):
    batch_id = clean_batch
    headers_supervisor = {
        "X-Actor-ID": "supervisor_1",
        "X-Actor-Role": "SUPERVISOR"
    }
    
    # Supervisor shouldn't be doing the work
    response = client.post(
        f"/batches/{batch_id}/event",
        json={"event": "progress_step", "step_id": "step-1"},
        headers=headers_supervisor
    )
    assert response.status_code == 403

def test_supervisor_can_approve_access(clean_batch):
    # This tests that Supervisor DOES NOT get 403 for approval.
    # It might get 409 (if state is wrong) or 200.
    batch_id = clean_batch
    headers_supervisor = {
        "X-Actor-ID": "supervisor_1",
        "X-Actor-Role": "SUPERVISOR"
    }
    
    response = client.post(
        f"/batches/{batch_id}/event",
        json={"event": "approve_step", "step_id": "step-1"},
        headers=headers_supervisor
    )
    # Assert NOT 403 (Access Denied)
    assert response.status_code != 403
