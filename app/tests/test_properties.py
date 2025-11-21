from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_property():
    response = client.post("/properties/", json={"name": "Bambili Hostel"})
    assert response.status_code == 200
    assert response.json()["name"] == "Bambili Hostel"
