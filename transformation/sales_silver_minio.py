# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

import pandas as pd
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from os import getenv


MINIO_ENDPOINT = getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = getenv("MINIO_SECURE", "false").lower() == "true"


def get_minio_client():
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def download_from_minio(client, bucket: str, object_name: str, file_path: str):
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(bucket, object_name, file_path)
        print(f"Downloaded from MinIO: {bucket}/{object_name} -> {file_path}")
    except S3Error as e:
        print(f"MinIO download error: {e}")
        raise


def upload_to_minio(client, bucket: str, object_name: str, file_path: str):
    try:
        client.fput_object(bucket, object_name, file_path)
        print(f"Uploaded to MinIO: {bucket}/{object_name}")
    except S3Error as e:
        print(f"MinIO upload error: {e}")
        raise


def transform():
    minio_client = get_minio_client()

    bronze_local = "data/bronze/sales/sales.csv"
    silver_local = "data/silver/sales/sales_clean.csv"
    gold_local = "data/gold/sales_daily.csv"

    print("Downloading bronze data from MinIO...")
    download_from_minio(minio_client, "bronze", "sales/sales.csv", bronze_local)

    df = pd.read_csv(bronze_local)
    print(f"Loaded {len(df)} records from bronze")

    # Remove duplicate transactions
    df = df.drop_duplicates(subset=["transaction_id"])

    # Convert date
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Remove invalid values
    df = df[(df["quantity"] > 0) & (df["unit_price"] >= 0)]

    # Calculate amount
    df["total_amount"] = df["quantity"] * df["unit_price"]

    # Save silver
    Path(silver_local).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(silver_local, index=False)
    print(f"Silver records: {len(df)}")

    upload_to_minio(minio_client, "silver", "sales/sales_clean.csv", silver_local)

    # Create gold daily aggregation
    gold_df = (
        df.groupby("transaction_date")
        .agg(
            transaction_count=("transaction_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("total_amount", "sum"),
        )
        .reset_index()
    )

    gold_df.to_csv(gold_local, index=False)
    print(f"Gold records: {len(gold_df)}")

    upload_to_minio(minio_client, "gold", "sales/sales_daily.csv", gold_local)

    print("Transformation completed successfully")


if __name__ == "__main__":
    transform()