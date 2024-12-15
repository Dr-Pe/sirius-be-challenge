from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # System parameters
    max_quota_in_gb: int
    # Default users and passwords
    default_admin_user: str
    default_admin_password: str
    default_non_admin_user: str
    default_non_admin_password: str
    # DB
    sqlite_filename: str
    # JWT
    secret_key: str
    access_token_expire_minutes: int
    # AWS
    aws_url: str
    aws_access_key: str
    aws_secret_key: str
    # Minio
    minio_url: str
    minio_access_key: str
    minio_secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


SETTINGS = Settings()
