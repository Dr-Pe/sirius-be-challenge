from minio import Minio
from src.models import *
import os


class FileStorageManager:

    def __init__(self, params: list[FileStorageClientParams]):
        self.clients = []
        for param in params:
            self.clients.append(FileStorageClient(param.endpoint, param.access_key, param.secret_key))

    def create_bucket(self, bucket_name):
        for client in self.clients:
            client.create_bucket(bucket_name)

    def destroy_bucket(self, bucket_name):
        for client in self.clients:
            client.destroy_bucket(bucket_name)

    def upload_file(self, bucket_name, file_path, filename):
        response = None
        for client in self.clients:
            with open(file_path, "rb") as file:
                response = self._upload_file(client, bucket_name, filename, file, os.fstat(file.fileno()).st_size)

        return response
    
    def list_files(self, bucket_name):
        for client in self.clients:
            return client.list_files(bucket_name)

    def download_file(self, bucket_name, file_path, filename):
        for client in self.clients:
            try:
                client.download_file(bucket_name, file_path, filename)
                break
            except Exception as e:
                print(e)
                continue

    def delete_file(self, bucket_name, filename):
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

    def download_file(self, bucket_name, file_path, filename):
        self.client.download_file(bucket_name, file_path, filename)

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

    def download_file(self, bucket_name, file_path, filename):
        self.client.fget_object(bucket_name, filename, file_path)

    def delete_file(self, bucket_name, filename):
        self.client.remove_object(bucket_name, filename)

    def get_bucket_size(self, bucket_name):
        total_size = 0
        for obj in self.client.list_objects(bucket_name, recursive=True):
            total_size += obj.size

        return total_size
