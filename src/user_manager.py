from fastapi import HTTPException
from sqlmodel import Session, update, select
import models
from db import engine, get_db_user, insert_model_instance
from file_storage_client import FileStorageClient
from settings import SETTINGS
from security import get_password_hash
from datetime import date


def create_user(user_dto: models.CreateUserDTO, fs_client: FileStorageClient):
    if get_db_user(user_dto.username):
        raise HTTPException(status_code=400, detail="User already exists")

    user_in_db = models.User(
        username=user_dto.username,
        password=get_password_hash(user_dto.password),
        is_admin=user_dto.is_admin,
    )
    insert_model_instance(user_in_db)
    fs_client.create_bucket(user_dto.username)

    return user_dto


class UserManager:

    def __init__(self, user: models.User):
        self.user = user

    def upload_file(self, fs_client, file_path, file_name):
        if self._can_upload_file():
            fs_upload_response_dto = fs_client.upload_file(
                self.user.username, file_path, file_name)
            self._update_user_quota(fs_upload_response_dto.new_bucket_size)
            self._update_user_daily_usage(fs_upload_response_dto.file_size)

            return fs_upload_response_dto
        else:
            return False
        
    def download_file(self, fs_client, file_path, file_name):
        fs_client.download_file(self.user.username, file_path, file_name)
        
    def delete_file(self, fs_client, file_name):
        new_quota = fs_client.delete_file(self.user.username, file_name)
        self._update_user_quota(new_quota)

        return new_quota

    def _can_upload_file(self):
        return self.user.quota < SETTINGS.max_quota_in_gb

    def _update_user_quota(self, new_quota):
        with Session(engine) as session:
            session.exec(update(models.User).where(
                models.User.username == self.user.username).values(quota=new_quota))
            session.commit()

    def _update_user_daily_usage(self, usage):
        with Session(engine) as session:
            daily_usage = session.exec(select(models.DailyUsage).where(
                models.DailyUsage.user_id == self.user.id)).one_or_none()
            if daily_usage and daily_usage.date == date.today():
                daily_usage.usage += usage
                session.exec(update(models.DailyUsage).where(
                    models.DailyUsage.user_id == self.user.id).values(usage=daily_usage.usage))
            elif daily_usage:
                session.exec(update(models.DailyUsage).where(
                    models.DailyUsage.user_id == self.user.id).values(date=date.today(), usage=usage))
            else:
                session.add(models.DailyUsage(
                    user_id=self.user.id, date=date.today(), usage=usage))

            session.commit()