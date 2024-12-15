from pydantic import BaseModel

class FileStorageResponseDTO(BaseModel):
    file_size: int
    new_bucket_size: int