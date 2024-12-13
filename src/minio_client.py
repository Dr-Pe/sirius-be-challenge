from minio import Minio

class MinioClient:
    
    def __init__(self, endpoint, access_key, secret_key):
        self.client = Minio(endpoint, access_key, secret_key, secure=False)

    def upload_file(self, bucket_name, file_path, file_name):
        found = self.client.bucket_exists(bucket_name)
        if not found:
            self.client.make_bucket(bucket_name)
            print(f"Bucket {bucket_name} created")
        else:
            print(f"Bucket {bucket_name} already exists")

        self.client.fput_object(bucket_name, file_name, file_path)
        print(f"File {file_name} uploaded to {bucket_name}")