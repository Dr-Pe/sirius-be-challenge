from fastapi import File, HTTPException
from fastapi.responses import StreamingResponse
from minio import Minio
from app.models import *


class FileStorageManager:

    def __init__(self, params: list[FileStorageClientParams]):
        self.clients = []
        for param in params:
            self.clients.append(FileStorageClient(param.endpoint, param.access_key, param.secret_key))

    def create_bucket(self, bucket_name: str):
        for client in self.clients:
            client.create_bucket(bucket_name)

    def destroy_bucket(self, bucket_name: str):
        for client in self.clients:
            client.destroy_bucket(bucket_name)

    def upload_file(self, bucket_name: str, file: File) -> FileStorageUploadResponseDTO:
        response = None
        for client in self.clients:
            try:
                response = client.upload_file(bucket_name, file.filename, file.file, file.size)
                file.file.seek(0)
            except Exception as e:
                raise HTTPException(status_code=400, detail={"detail": str(e)})

        return response

    def list_files(self, bucket_name: str) -> list[FileStorageFileDTO]:
        for client in self.clients:
            return client.list_files(bucket_name)

    def download_file(self, bucket_name: str, filename: str) -> StreamingResponse:
        for client in self.clients:
            try:
                return StreamingResponse(client.download_file(bucket_name, filename), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}"})
            except Exception as e:
                print(e)
                continue

    def delete_file(self, bucket_name: str, filename: str) -> int:
        new_quota = None
        for client in self.clients:
            new_quota = client.delete_file(bucket_name, filename)

        return new_quota

    def _upload_file(self, client, bucket_name, filename, file, file_size):
        return client.upload_file(bucket_name, filename, file, file_size)


class FileStorageClient:

    def __init__(self, endpoint, access_key, secret_key):
        self.client = MinioS3Client(endpoint, access_key, secret_key)

    def create_bucket(self, bucket_name):
        self.client.create_bucket(bucket_name)

    def destroy_bucket(self, bucket_name):
        self.client.destroy_bucket(bucket_name)

    def upload_file(self, bucket_name, filename, file, file_size):
        old_bucket_size = self.client.get_bucket_size(bucket_name)
        self.client.upload_file(bucket_name, filename, file, file_size)
        new_bucket_size = self.client.get_bucket_size(bucket_name)

        return FileStorageUploadResponseDTO(file_size=new_bucket_size - old_bucket_size, new_bucket_size=new_bucket_size)

    def list_files(self, bucket_name):
        return self.client.list_files(bucket_name)

    def download_file(self, bucket_name, filename):
        return self.client.download_file(bucket_name, filename)

    def delete_file(self, bucket_name, filename):
        self.client.delete_file(bucket_name, filename)
        return self.client.get_bucket_size(bucket_name)


class MinioS3Client:

    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(endpoint, access_key, secret_key, secure=False)

    def create_bucket(self, bucket_name):
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} created")
        else:
            print(f"Bucket {bucket_name} already exists")

    def destroy_bucket(self, bucket_name):
        self.client.remove_bucket(bucket_name)

    def upload_file(self, bucket_name, filename, file, file_size):
        self.client.put_object(bucket_name, filename, file, file_size)

    def list_files(self, bucket_name):
        return self.client.list_objects(bucket_name)

    def download_file(self, bucket_name, filename):
        return self.client.get_object(bucket_name, filename)

    def delete_file(self, bucket_name, filename):
        self.client.remove_object(bucket_name, filename)

    def get_bucket_size(self, bucket_name):
        total_size = 0
        for obj in self.client.list_objects(bucket_name, recursive=True):
            total_size += obj.size

        return total_size
