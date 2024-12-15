from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException
from src.models import CreateUserDTO, GetUserDTO, User
from src.db import get_db_users
from src.security import get_current_user
from src.user_manager import create_user
from src.dependencies import fs_manager

router = APIRouter()

@router.post("/users/")
async def post_user(user_dto: CreateUserDTO) -> User:
    return create_user(user_dto, fs_manager)


@router.get("/users/")
async def get_users(current_user: Annotated[User, Depends(get_current_user)]) -> list[GetUserDTO]:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users_in_db = get_db_users()

    return [GetUserDTO.from_orm(user) for user in users_in_db]


@router.get("/users/me/")
async def get_users_me(current_user: Annotated[User, Depends(get_current_user)]) -> GetUserDTO:
    return GetUserDTO.from_orm(current_user)