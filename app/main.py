from fastapi import FastAPI

from app import routers
from app.internal.db import create_db_and_tables, get_db_user
from app.internal.dependencies import fs_manager
from app.internal.user_manager import create_user
from app.models import *
from app.settings import SETTINGS

app = FastAPI()

app.include_router(routers.users.router)
app.include_router(routers.files.router)
app.include_router(routers.other.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    if not get_db_user(SETTINGS.default_admin_user):
        admin = User(username=SETTINGS.default_admin_user,
                     password=SETTINGS.default_admin_password, is_admin=True)
        create_user(admin, fs_manager)
    if not get_db_user(SETTINGS.default_non_admin_user):
        noadmin = User(username=SETTINGS.default_non_admin_user,
                       password=SETTINGS.default_non_admin_password, is_admin=False)
        create_user(noadmin, fs_manager)
