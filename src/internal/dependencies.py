from src.models import FileStorageClientParams
from src.settings import SETTINGS

from .file_storage_manager import FileStorageManager

fs_manager = FileStorageManager([
    FileStorageClientParams(endpoint=SETTINGS.minio_url,
                            access_key=SETTINGS.minio_access_key, secret_key=SETTINGS.minio_secret_key),
    FileStorageClientParams(endpoint=SETTINGS.aws_url,
                            access_key=SETTINGS.aws_access_key, secret_key=SETTINGS.aws_secret_key)
])
