from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlite_filename: str
    secret_key: str
    access_token_expire_minutes: int
    minio_url: str
    minio_access_key: str
    minio_secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


SETTINGS = Settings()
