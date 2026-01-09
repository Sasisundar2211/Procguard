import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sop():
    return {
        "id": "proc-1",
        "steps": [
            {"id": "1", "description": "Login"},
            {"id": "2", "description": "Verify batch"},
            {"id": "3", "description": "Supervisor approval"}
        ]
    }

@pytest.fixture
def role_map():
    return {
        "1": "operator",
        "2": "operator",
        "3": "supervisor"
    }
