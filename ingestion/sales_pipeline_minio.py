# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

import pandas as pd
from sqlalchemy import create_engine, text
from minio import Minio
from minio.error import S3Error
from os import getenv
from pathlib import Path


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"dataeng:{getenv('PGPASSWORD', 'dataeng')}"
    f"@{getenv('DB_HOST', 'postgres')}:5432/datawarehouse"
)

MINIO_ENDPOINT = getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = getenv("MINIO_SECURE", "false").lower() == "true"

CSV_FILE = "data/raw/sales.csv"


def get_minio_client():
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_minio_buckets(client):
    buckets = ["bronze", "silver", "gold"]
    for bucket in buckets:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f"Created bucket: {bucket}")


def upload_to_minio(client, bucket: str, object_name: str, file_path: str):
    try:
        client.fput_object(bucket, object_name, file_path)
        print(f"Uploaded to MinIO: {bucket}/{object_name}")
    except S3Error as e:
        print(f"MinIO upload error: {e}")
        raise


def extract():
    return pd.read_csv(CSV_FILE)


def validate(df):
    required_columns = [
        "transaction_id",
        "transaction_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    if df["transaction_id"].duplicated().any():
        raise ValueError("Duplicate transaction_id found")

    if (df["quantity"] <= 0).any():
        raise ValueError("Quantity must be greater than zero")

    if (df["unit_price"] < 0).any():
        raise ValueError("Unit price cannot be negative")

    return True


def transform(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["total_amount"] = df["quantity"] * df["unit_price"]
    return df


def load_to_postgres(df):
    engine = create_engine(DATABASE_URL)
    columns = [
        "transaction_id",
        "transaction_date",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
    ]
    df[columns].to_sql(
        "sales",
        engine,
        schema="raw",
        if_exists="append",
        index=False,
    )
    print(f"Loaded {len(df)} records to PostgreSQL raw.sales")


def load_to_minio(df, client):
    bronze_path = "data/bronze/sales/sales.csv"
    Path(bronze_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(bronze_path, index=False)
    upload_to_minio(client, "bronze", "sales/sales.csv", bronze_path)


def main():
    print("=== Starting Ingestion Pipeline ===")

    minio_client = get_minio_client()
    ensure_minio_buckets(minio_client)

    print("Extract")
    df = extract()
    print(f"Extracted {len(df)} records")

    print("Validate")
    validate(df)

    print("Transform")
    df = transform(df)

    print("Load to PostgreSQL")
    load_to_postgres(df)

    print("Load to MinIO Data Lake")
    load_to_minio(df, minio_client)

    print("=== Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()