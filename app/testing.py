from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.settings import SETTINGS

client = TestClient(app)


# ================================
#                           utils
# ================================

def _get_token(username, password):
    response = client.post(
        "/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _post_file(token, filename):
    # Create a file-like object (BytesIO) that mimics the behavior of a file
    file = BytesIO(b"This is a test file")
    file.name = filename  # Set the file name

    response = client.post("/files/", files={"file": (file.name, file, "text/plain")},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def _delete_file(token, filename):
    response = client.delete("/files/" + filename, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def _post_then_delete_file(username, password, filename):
    token = _get_token(username, password)

    _post_file(token, filename)
    _delete_file(token, filename)

# ================================
#                   users routers
# ================================

def test_post_existent_user_as_unauth():
    response = client.post(
        "/users/", json={"username": SETTINGS.default_admin_user, "password": SETTINGS.default_admin_password, "is_admin": True})
    assert response.status_code == 400


def test_post_then_delete_user():
    username = "new-user"
    password = "new_user_password"

    response = client.post("/users/", json={"username": username, "password": password, "is_admin": False})
    assert response.status_code == 200

    response = client.post("/users/", json={"username": username, "password": password, "is_admin": False})
    assert response.status_code == 400

    token = _get_token(username, password)
    response = client.delete(f"/users/{username}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_get_as_unauth():
    response = client.get("/users/")
    assert response.status_code == 401


def test_get_as_noadmin():
    token = _get_token(SETTINGS.default_non_admin_user, SETTINGS.default_non_admin_password)

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    response = client.get("/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == SETTINGS.default_non_admin_user
    assert response.json()["is_admin"] == False


def test_get_as_admin():
    token = _get_token(SETTINGS.default_admin_user, SETTINGS.default_admin_password)

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

    response = client.get("/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == SETTINGS.default_admin_user
    assert response.json()["is_admin"] == True


# ================================
#                   files routers
# ================================

def test_post_then_delete_file():
    filename = "test-file.txt"

    # As admin
    _post_then_delete_file(SETTINGS.default_admin_user, SETTINGS.default_admin_password, filename)

    # As noadmin
    _post_then_delete_file(SETTINGS.default_non_admin_user, SETTINGS.default_non_admin_password, filename)


def test_list_files_n_stats():
    token = _get_token(SETTINGS.default_admin_user, SETTINGS.default_admin_password)

    response = client.get("/files/list", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    cant_files = len(response.json())
    _post_file(token, "test-file-1.txt")
    _post_file(token, "test-file-2.txt")

    response = client.get("/files/list", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == cant_files + 2

    _delete_file(token, "test-file-1.txt")
    response = client.get("/files/list", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == cant_files + 1

    _delete_file(token, "test-file-2.txt")
    response = client.get("/files/list", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == cant_files

    response = client.get("/stats/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0 # At least the admin user, at least because of this test

