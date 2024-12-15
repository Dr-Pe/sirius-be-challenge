from typing import Annotated
from fastapi import Depends, HTTPException
from src.models import *
from src.security import get_current_user
from src.user_manager import UserManager
from src.dependencies import fs_manager
from fastapi import APIRouter

router = APIRouter()


@router.post("/files/")
async def post_file(filepath: str, filename: str, current_user: Annotated[User, Depends(get_current_user)]):
    if UserManager(current_user).upload_file(fs_manager, filepath, filename):
        return {"detail": "File uploaded"}
    else:
        raise HTTPException(status_code=400, detail="Quota exceeded")


@router.get("/files/")
async def get_file(filepath: str, filename: str, current_user: Annotated[User, Depends(get_current_user)]):
    UserManager(current_user).download_file(fs_manager, filepath, filename)


@router.delete("/files/{filename}")
async def delete_file(filename: str, current_user: Annotated[User, Depends(get_current_user)]):
    if UserManager(current_user).delete_file(fs_manager, filename):
        return {"detail": "File deleted"}
    else:
        raise HTTPException(status_code=400, detail="File not found")