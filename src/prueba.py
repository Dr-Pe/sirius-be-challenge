from minio import Minio
from settings import SETTINGS

# client = boto3.client('s3', aws_access_key_id=SETTINGS.aws_access_key, aws_secret_access_key=SETTINGS.aws_secret_key)
client = Minio('s3.amazonaws.com', SETTINGS.aws_access_key, SETTINGS.aws_secret_key)

print(client.list_buckets())