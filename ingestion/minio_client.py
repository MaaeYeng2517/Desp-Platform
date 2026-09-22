# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

from minio import Minio
from minio.error import S3Error
from os import getenv


class DataLakeClient:
    def __init__(self):
        self.client = Minio(
            endpoint=getenv("MINIO_ENDPOINT", "localhost:9000"),
            access_key=getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=getenv("MINIO_SECRET_KEY", "minioadmin"),
            secure=getenv("MINIO_SECURE", "false").lower() == "true",
        )

    def ensure_buckets(self):
        buckets = ["bronze", "silver", "gold"]
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                print(f"Created bucket: {bucket}")
            else:
                print(f"Bucket exists: {bucket}")

    def upload_file(self, bucket: str, object_name: str, file_path: str):
        try:
            self.client.fput_object(bucket, object_name, file_path)
            print(f"Uploaded {file_path} to {bucket}/{object_name}")
        except S3Error as e:
            print(f"Error uploading to MinIO: {e}")
            raise

    def download_file(self, bucket: str, object_name: str, file_path: str):
        try:
            self.client.fget_object(bucket, object_name, file_path)
            print(f"Downloaded {bucket}/{object_name} to {file_path}")
        except S3Error as e:
            print(f"Error downloading from MinIO: {e}")
            raise

    def list_objects(self, bucket: str, prefix: str = ""):
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects: {e}")
            return []


def main():
    dl = DataLakeClient()
    dl.ensure_buckets()


if __name__ == "__main__":
    main()