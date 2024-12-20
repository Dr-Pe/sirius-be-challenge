from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.internal.db import get_db_users_w_stats
from app.internal.security import (authenticate_user, create_access_token,
                                   get_current_user)
from app.models import *

router = APIRouter()


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"},)

    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@router.get("/stats/")
async def get_stats(current_user: Annotated[User, Depends(get_current_user)]) -> list[GetUserStatsDTO]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = get_db_users_w_stats()

    return [GetUserStatsDTO.from_orm(user) for user in users_in_db if user.daily_usage]
