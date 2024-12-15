from fastapi.testclient import TestClient
from settings import SETTINGS
from main import app, fs_client
from io import BytesIO

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
    # TODO: I souldn't be using the 'private' of fs_client method here, but the public one, in order to test also the calculation of the new quota and daily usage
    test_file = BytesIO(b"test file content")
    fs_client._upload_file(
        SETTINGS.default_admin_user, "test_file.txt", test_file, test_file.getbuffer().nbytes)
    
    response = client.post(
        "/token", data={"username": SETTINGS.default_admin_user, "password": SETTINGS.default_admin_password})  
    token = response.json()["access_token"]

    response = client.delete("/files/test_file.txt", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
