from fastapi.testclient import TestClient
from models.settings import SETTINGS
from main import app
import os

client = TestClient(app)


def test_post_existent_user():
    response = client.post(
        "/users/", json={"username": SETTINGS.default_admin_user, "password": SETTINGS.default_admin_password, "is_admin": True})
    assert response.status_code == 400


def test_get_as_unauth():
    response = client.get("/users/")
    assert response.status_code == 401


def test_get_as_noadmin():
    response = client.post(
        "/token", data={"username": SETTINGS.default_non_admin_user, "password": SETTINGS.default_non_admin_password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    response = client.get(
        "/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_get_as_admin():
    response = client.post(
        "/token", data={"username": SETTINGS.default_admin_user, "password": SETTINGS.default_admin_password})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.get(
        "/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_post_as_unauth():
    this_file_path = os.path.abspath(__file__)
    filename_in_storage = os.path.basename(this_file_path)
    response = client.post(
        "/files/", data={"filepath": this_file_path, "filename": filename_in_storage})
    assert response.status_code == 401
