import datetime

from pydantic import BaseModel


class FileStorageUploadResponseDTO(BaseModel):
    file_size: int
    new_bucket_size: int

class FileStorageFileDTO(BaseModel):
    name: str
    last_modified: datetime.datetime
    size: int

    def from_s3file_object(s3file):
        return FileStorageFileDTO(
            name=s3file._object_name,
            last_modified=s3file._last_modified,
            size=s3file._size
        )

class FileStorageClientParams(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str

