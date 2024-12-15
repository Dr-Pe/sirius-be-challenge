from minio import Minio
from models import FileStorageResponseDTO
import os


class FileStorageClient:

    def __init__(self, endpoint, access_key, secret_key):
        # TODO: This should be dynamic
        self.client = MinioClient(endpoint, access_key, secret_key)

    def create_bucket(self, username):
        self.client.create_bucket(username)

    def upload_file(self, username, file_path, file_name):
        old_bucket_size = self.client.get_bucket_size(username)
        with open(file_path, "rb") as file:
            self._upload_file(
                username, file_name, file, os.fstat(file.fileno()).st_size)
        
        new_bucket_size = self.client.get_bucket_size(username)

        return FileStorageResponseDTO(file_size=new_bucket_size - old_bucket_size, new_bucket_size=new_bucket_size)

    def download_file(self, username, file_path, file_name):
        self.client.download_file(username, file_path, file_name)

    def delete_file(self, username, file_name):
        self.client.delete_file(username, file_name)
        return self.client.get_bucket_size(username)
    
    def _upload_file(self, bucket_name, file_name, file, file_size):
        self.client.upload_file(bucket_name, file_name, file, file_size)


class MinioClient:

    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(endpoint, access_key, secret_key, secure=False)

    def create_bucket(self, bucket_name):
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} created")
        else:
            print(f"Bucket {bucket_name} already exists")

    def upload_file(self, bucket_name, file_name, file, file_size):
        self.create_bucket(bucket_name)
        self.client.put_object(bucket_name, file_name, file, file_size)

    def download_file(self, bucket_name, file_path, file_name):
        self.client.fget_object(bucket_name, file_name, file_path)

    def delete_file(self, bucket_name, file_name):
        self.client.remove_object(bucket_name, file_name)

    def get_bucket_size(self, bucket_name):
        total_size = 0
        for obj in self.client.list_objects(bucket_name, recursive=True):
            total_size += obj.size

        return total_size
