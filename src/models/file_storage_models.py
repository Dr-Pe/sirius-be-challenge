from pydantic import BaseModel

class FileStorageResponseDTO(BaseModel):
    file_size: int
    new_bucket_size: int

class FileStorageClientParams(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str