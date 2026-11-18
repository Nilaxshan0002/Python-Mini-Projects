from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_endpoint():
    response = client.post(
        "/api/endpoints/",
        json={"name": "Test API", "url": "https://jsonplaceholder.typicode.com/posts/1"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test API"