import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Note: Testing the actual run_task endpoint requires an OpenAI API key 
# and will launch a real browser, so it's usually mocked in unit tests.