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


def _post_then_delete_file(token):
    # Create a file-like object (BytesIO) that mimics the behavior of a file
    file = BytesIO(b"This is a test file")
    file.name = "testfile.txt"  # Set the file name


    response = client.post("/files/", files={"file": (file.name, file, "text/plain")}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = client.delete("/files/" + file.name, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


# ================================
#                   users routers
# ================================

def test_post_existent_user():
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
    # As admin
    token = _get_token(SETTINGS.default_admin_user, SETTINGS.default_admin_password)
    _post_then_delete_file(token)

    # As noadmin
    token = _get_token(SETTINGS.default_non_admin_user, SETTINGS.default_non_admin_password)
    _post_then_delete_file(token)
