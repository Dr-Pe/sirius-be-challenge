from fastapi.testclient import TestClient
from src.settings import SETTINGS
from src.main import app
import tempfile
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


def test_upload_then_delete_file_as_admin():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Write some content to the file
        temp_file.write(b"Some test content")
        temp_file_path = temp_file.name  # Get the file path to use in the test

    filename = os.path.basename(temp_file_path)

    response = client.post(
        "/token", data={"username": SETTINGS.default_admin_user, "password": SETTINGS.default_admin_password})
    token = response.json()["access_token"]

    response = client.post("/files/", params={"filepath": temp_file_path, "filename": filename},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.delete("/files/test_file.txt", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
