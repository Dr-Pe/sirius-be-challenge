from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_users_unauth():
    response = client.get("/users/")
    assert response.status_code == 401

def test_get_users_noadmin():
    response = client.post("/token", data={"username": "noadmin", "password": "user"})
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_get_users_admin():
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
