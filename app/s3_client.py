import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import HTTPException

load_dotenv()

class S3Client:
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key, bucket_name):
        self.s3 = boto3.client('s3', endpoint_url=endpoint_url,
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key)
        self.bucket_name = bucket_name

    def upload_file(self, file, file_name):
        try:
            self.s3.upload_fileobj(file, self.bucket_name, file_name)
            return f"{self.bucket_name}/{file_name}"
        except (NoCredentialsError, PartialCredentialsError):
            raise HTTPException(status_code=500, detail="Credentials not available")

    def upload_bytes(self, data, file_name):
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)
            return f"{self.bucket_name}/{file_name}"
        except (NoCredentialsError, PartialCredentialsError):
            raise HTTPException(status_code=500, detail="Credentials not available")

    def get_file_url(self, file_name):
        return f"{self.s3.meta.endpoint_url}/{self.bucket_name}/{file_name}"

    def delete_file(self, file_name):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error deleting file")

s3_client = S3Client(endpoint_url=os.getenv('MINIO_ENDPOINT'),
                     aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
                     aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
                     bucket_name=os.getenv('MINIO_BUCKET'))
