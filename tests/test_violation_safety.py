import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from app.main import app
from app.api.deps import get_db
from app.models.violation import Violation

client = TestClient(app)

def test_violation_not_found_returns_404():
    """
    Forensic Check: Missing violations must return 404, not 500.
    """
    # Use a mock database to avoid needing a real one for this test
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    random_id = uuid4()
    response = client.get(f"/violations/{random_id}")
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_violation_integrity_failure_returns_409():
    """
    Forensic Check: Violation without a batch (Orphan) must return 409.
    """
    violation_id = uuid4()
    batch_id = uuid4()
    
    # Use a real model object to satisfy Pydantic validation
    mock_violation = Violation(
        id=violation_id,
        batch_id=batch_id,
        rule="STEP_ORDER_VIOLATION",
        detected_at=datetime.utcnow(),
        status="OPEN",
        payload={"reason": "mock"}
    )
    # Simulate orphan
    mock_violation.batch = None
    
    # We need to mock the query return
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = mock_violation
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get(f"/violations/{violation_id}")
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 409
    assert "Integrity Failure" in response.json()["detail"]

def test_violation_detail_returns_404_for_unknown_id():
    """
    Forensic Check: A strictly unknown ID must return 404.
    """
    unknown_id = uuid4()
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get(f"/violations/{unknown_id}")
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 404
