from minio import Minio

class FileStorageClient:

    def __init__(self, endpoint, access_key, secret_key):
        # TODO: This should be dynamic
        self.client = MinioClient(endpoint, access_key, secret_key)

    def create_bucket(self, username):
        self.client.create_bucket(username)

    def upload_file(self, username, file_path, file_name):
        self.client.upload_file(username, file_path, file_name)
        return self.client.get_bucket_size(username)

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

    def upload_file(self, bucket_name, file_path, file_name):
        self.create_bucket(bucket_name)
        self.client.fput_object(bucket_name, file_name, file_path)

    def get_bucket_size(self, bucket_name):
        total_size = 0
        for obj in self.client.list_objects(bucket_name, recursive=True):
            total_size += obj.size
        
        return total_size