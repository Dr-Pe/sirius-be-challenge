from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

import models
from db import SessionDep, create_db_and_tables, insert_model_instance
from security import authenticate_user, create_access_token, get_password_hash, get_current_user
from minio_client import MinioClient
from models.settings import SETTINGS

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # TODO: Pasar user y password a variables de entorno
    admin = models.User(
        username="admin", password=get_password_hash("admin"), is_admin=True)
    noadmin = models.User(
        username="noadmin", password=get_password_hash("noadmin"), is_admin=False)
    insert_model_instance(admin)
    insert_model_instance(noadmin)


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
async def post_user(user: models.User) -> models.User:
    user_in_db = models.User(
        username=user.username,
        password=get_password_hash(user.password),
        is_admin=user.is_admin,
    )

    return insert_model_instance(user_in_db)


@app.get("/users/")
async def get_users(session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]) -> list[models.User]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = session.exec(select(models.User)).all()
    users = [user.clean() for user in users_in_db]

    return users


@app.get("/users/me/")
async def get_users_me(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    return current_user.clean()


@app.post("/files/")
async def post_file(filepath: str, filename: str):
    client = MinioClient(
        "127.0.0.1:9000", SETTINGS.minio_access_key, SETTINGS.minio_secret_key)
    client.upload_file("sirius", filepath, filename)
