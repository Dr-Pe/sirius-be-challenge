from sqlmodel import update, Session
from db import engine
import models
from models.settings import SETTINGS


class UserManager:

    def __init__(self, user: models.User):
        self.user = user

    def upload_file(self, fs_client, file_path, file_name):
        if self.user.quota < SETTINGS.max_quota_in_gb:
            new_quota = fs_client.upload_file(self.user.username, file_path, file_name)
            with Session(engine) as session:
                session.exec(update(models.User).where(models.User.username == self.user.username).values(quota=new_quota))
                session.commit()
            
            return new_quota
        else:
            return False

    def delete_file(self, fs_client, file_name):
        new_quota = fs_client.delete_file(self.user.username, file_name)
        with Session(engine) as session:
            session.exec(update(models.User).where(models.User.username == self.user.username).values(quota=new_quota))
            session.commit()

        return new_quota