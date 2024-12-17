from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.internal.dependencies import fs_manager
from app.internal.security import get_current_user
from app.internal.user_manager import UserManager
from app.models import *

router = APIRouter()


@router.post("/files/")
async def post_file(file: UploadFile, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    UserManager(current_user).upload_file(fs_manager, file)
    return {"detail": f"{file.filename} uploaded"}


@router.get("/files/")
async def get_file(filepath: str, filename: str, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    UserManager(current_user).download_file(fs_manager, filepath, filename)
    return {"detail": f"{filename} downloaded in {filepath}"}


@router.delete("/files/{filename}")
async def delete_file(filename: str, current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    UserManager(current_user).delete_file(fs_manager, filename)
    return {"detail": f"{filename} deleted for {current_user.username}"}


@router.post("/files/list")
async def list_files(current_user: Annotated[User, Depends(get_current_user)]) -> list[FileStorageFileDTO]:
    return UserManager(current_user).list_files(fs_manager)
