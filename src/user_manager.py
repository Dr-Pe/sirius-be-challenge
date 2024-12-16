from src.models import *
from fastapi import HTTPException
from sqlmodel import Session, update, select
from src.db import engine, get_db_user, insert_model_instance, delete_model_instance
from src.file_storage_manager import FileStorageClient
from src.settings import SETTINGS
from src.security import get_password_hash
from datetime import date
import uuid


def create_user(user_dto: CreateUserDTO, fs_client: FileStorageClient) -> GetUserDTO:
    if get_db_user(user_dto.username):
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = User(
        username=user_dto.username,
        password=get_password_hash(user_dto.password),
        is_admin=user_dto.is_admin,
        bucket_name=f"{user_dto.username}-{uuid.uuid4()}"
    )
    insert_model_instance(user_in_db)
    fs_client.create_bucket(user_in_db.bucket_name)

    return GetUserDTO.from_orm(user_in_db)


def destroy_user(username: str, fs_client: FileStorageClient):
    user = get_db_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_model_instance(user)
    fs_client.destroy_bucket(user.bucket_name)

    return {"detail": f"User {username} deleted"}


class UserManager:

    def __init__(self, user: User):
        self.user = user

    def upload_file(self, fs_manager, file_path, filename):
        if self._can_upload_file():
            fs_upload_response_dto = fs_manager.upload_file(
                self.user.bucket_name, file_path, filename)
            self._update_user_quota(fs_upload_response_dto.new_bucket_size)
            self._update_user_daily_usage(fs_upload_response_dto.file_size)

            return fs_upload_response_dto
        else:
            return False

    def list_files(self, fs_manager):
        return [FileStorageFileDTO.from_s3file_object(file) for file in fs_manager.list_files(self.user.bucket_name)]

    def download_file(self, fs_manager, file_path, filename):
        fs_manager.download_file(self.user.bucket_name, file_path, filename)

    def delete_file(self, fs_manager, filename):
        new_quota = fs_manager.delete_file(self.user.bucket_name, filename)
        self._update_user_quota(new_quota)

    def _can_upload_file(self):
        return self.user.quota < SETTINGS.max_quota_in_gb

    def _update_user_quota(self, new_quota):
        with Session(engine) as session:
            session.exec(update(User).where(
                User.username == self.user.username).values(quota=new_quota))
            session.commit()

    def _update_user_daily_usage(self, usage):
        with Session(engine) as session:
            daily_usage = session.exec(select(DailyUsage).where(
                DailyUsage.user_id == self.user.id)).one_or_none()
            if daily_usage and daily_usage.date == date.today():
                daily_usage.usage += usage
                session.exec(update(DailyUsage).where(
                    DailyUsage.user_id == self.user.id).values(usage=daily_usage.usage))
            elif daily_usage:
                session.exec(update(DailyUsage).where(
                    DailyUsage.user_id == self.user.id).values(date=date.today(), usage=usage))
            else:
                session.add(DailyUsage(
                    user_id=self.user.id, date=date.today(), usage=usage))

            session.commit()
