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
    
    # Create batch
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

def test_operator_cannot_approve(clean_batch):
    batch_id = clean_batch
    headers_operator = {
        "X-Actor-ID": "operator_1",
        "X-Actor-Role": "OPERATOR"
    }
    
    # Need to be in a state where APPROVE might be valid?
    # Or regardless of state, Operator is forbidden.
    # Current state is IN_PROGRESS.
    
    response = client.post(
        f"/batches/{batch_id}/event",
        json={"event": "approve_step", "step_id": "step-1"},
        headers=headers_operator
    )
    assert response.status_code == 403

def test_operator_cannot_reject(clean_batch):
    batch_id = clean_batch
    headers_operator = {
        "X-Actor-ID": "operator_1",
        "X-Actor-Role": "OPERATOR"
    }
    
    response = client.post(
        f"/batches/{batch_id}/event",
        json={"event": "reject_batch"},
        headers=headers_operator
    )
    assert response.status_code == 403
