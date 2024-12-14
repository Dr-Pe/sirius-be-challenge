from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

import models
from db import SessionDep, create_db_and_tables, get_user
from file_storage_client import FileStorageClient
from models.settings import SETTINGS
from security import authenticate_user, create_access_token, get_current_user
from utils import create_user

app = FastAPI()
fs_client = FileStorageClient(
    SETTINGS.minio_url, SETTINGS.minio_access_key, SETTINGS.minio_secret_key)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # TODO: Pasar user y password a variables de entorno
    if not get_user("admin"):
        admin = models.User(
            username="admin", password="admin", is_admin=True)
        create_user(admin, fs_client)
    if not get_user("noadmin"):
        noadmin = models.User(
            username="noadmin", password="noadmin", is_admin=False)
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


@app.post("/user/")
async def post_user(user_dto: models.CreateUserDTO) -> models.User:
    return create_user(user_dto, fs_client)


@app.get("/users/")
async def get_users(session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]) -> list[models.GetUserDTO]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = session.exec(select(models.User)).all()

    return [models.GetUserDTO.from_orm(user) for user in users_in_db]


@app.get("/users/me/")
async def get_users_me(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.GetUserDTO:
    return models.GetUserDTO.from_orm(current_user)


@app.post("/files/")
async def post_file(filepath: str, filename: str, current_user: Annotated[models.User, Depends(get_current_user)]):
    return fs_client.upload_file(current_user.username, filepath, filename)


