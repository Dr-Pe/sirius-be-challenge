from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import models
from db import create_db_and_tables, get_db_user, get_db_users, get_db_users_w_stats
from file_storage_manager import FileStorageClient
from settings import SETTINGS
from security import authenticate_user, create_access_token, get_current_user
from user_manager import create_user, UserManager

app = FastAPI()
fs_client = FileStorageClient(
    SETTINGS.minio_url, SETTINGS.minio_access_key, SETTINGS.minio_secret_key)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    if not get_db_user(SETTINGS.default_admin_user):
        admin = models.User(username=SETTINGS.default_admin_user,
                            password=SETTINGS.default_admin_password, is_admin=True)
        create_user(admin, fs_client)
    if not get_db_user(SETTINGS.default_non_admin_user):
        noadmin = models.User(username=SETTINGS.default_non_admin_user,
                              password=SETTINGS.default_non_admin_password, is_admin=False)
        create_user(noadmin, fs_client)


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)

    access_token = create_access_token(data={"sub": user.username})

    return models.Token(access_token=access_token, token_type="bearer")


@app.post("/users/")
async def post_user(user_dto: models.CreateUserDTO) -> models.User:
    return create_user(user_dto, fs_client)


@app.get("/users/")
async def get_users(current_user: Annotated[models.User, Depends(get_current_user)]) -> list[models.GetUserDTO]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = get_db_users()

    return [models.GetUserDTO.from_orm(user) for user in users_in_db]


@app.get("/users/me/")
async def get_users_me(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.GetUserDTO:
    return models.GetUserDTO.from_orm(current_user)


@app.post("/files/")
async def post_file(filepath: str, filename: str, current_user: Annotated[models.User, Depends(get_current_user)]):
    if UserManager(current_user).upload_file(fs_client, filepath, filename):
        return {"detail": "File uploaded"}
    else:
        raise HTTPException(status_code=400, detail="Quota exceeded")

@app.get("/files/")
async def get_file(filepath: str, filename: str, current_user: Annotated[models.User, Depends(get_current_user)]):
    UserManager(current_user).download_file(fs_client, filepath, filename)

@app.delete("/files/{filename}")
async def delete_file(filename: str, current_user: Annotated[models.User, Depends(get_current_user)]):
    if UserManager(current_user).delete_file(fs_client, filename):
        return {"detail": "File deleted"}
    else:
        raise HTTPException(status_code=400, detail="File not found")

@app.get("/stats/")
async def get_stats(current_user: Annotated[models.User, Depends(get_current_user)]) -> list[models.GetUserStatsDTO]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = get_db_users_w_stats()

    return [models.GetUserStatsDTO.from_orm(user) for user in users_in_db if user.daily_usage]