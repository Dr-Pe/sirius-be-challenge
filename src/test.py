from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_post_existent_user():
    response = client.post("/user/", json={"username": "admin", "password": "admin", "is_admin": True})
    assert response.status_code == 400

def test_get_as_unauth():
    response = client.get("/users/")
    assert response.status_code == 401

def test_get_as_noadmin():
    response = client.post("/token", data={"username": "noadmin", "password": "noadmin"})
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_get_as_admin():
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_post_as_unauth():
    response = client.post("/files/", data={"filepath": "test", "filename": "test"})
    assert response.status_code == 401
