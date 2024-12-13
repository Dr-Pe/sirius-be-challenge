from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

import models
from db import SessionDep, create_db_and_tables
from security import authenticate_user, create_access_token, get_password_hash, get_current_user
from minio_client import MinioClient
from settings import SETTINGS

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)

    access_token = create_access_token(data={"sub": user.username})

    return models.Token(access_token=access_token, token_type="bearer")


@app.post("/user/")
async def post_user(user: models.User, session: SessionDep) -> models.User:
    user_in_db = models.User(
        username=user.username,
        password=get_password_hash(user.password),
        is_admin=user.is_admin,
    )
    session.add(user_in_db)
    session.commit()
    session.refresh(user_in_db)

    return user


@app.get("/users/")
async def get_users(session: SessionDep) -> list[models.User]:
    users_in_db = session.exec(select(models.User)).all()
    users = [user.clean() for user in users_in_db]

    return users


@app.get("/users/me/")
async def get_users_me(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    return current_user.clean()

@app.post("/files/")
async def post_file(filepath: str, filename: str):
    client = MinioClient("127.0.0.1:9000", SETTINGS.minio_access_key, SETTINGS.minio_secret_key)
    client.upload_file("sirius", filepath, filename)
