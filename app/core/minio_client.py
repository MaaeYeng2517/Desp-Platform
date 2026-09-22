from minio import Minio
from app.core.config import settings


def get_minio_client() -> Minio:
    return Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket(client: Minio, bucket_name: str) -> None:
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket: {bucket_name}")
    else:
        print(f"Bucket exists: {bucket_name}")


def ensure_all_buckets(client: Minio) -> None:
    for bucket in [
        settings.MINIO_BUCKET_BRONZE,
        settings.MINIO_BUCKET_SILVER,
        settings.MINIO_BUCKET_GOLD,
    ]:
        ensure_bucket(client, bucket)
