from fastapi import FastAPI

from src import routers
from src.internal.db import create_db_and_tables, get_db_user
from src.internal.dependencies import fs_manager
from src.models import *
from src.settings import SETTINGS
from src.internal.user_manager import create_user

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
