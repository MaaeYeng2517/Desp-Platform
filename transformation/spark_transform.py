# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Spark-based transformation for large-scale data processing.

This module provides Spark jobs for transforming data at scale,
reading from MinIO (Data Lake) and writing back to MinIO.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, to_date
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DateType,
    IntegerType,
    DecimalType,
)
from minio import Minio
from os import getenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# MinIO Configuration
MINIO_ENDPOINT = getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = getenv("MINIO_SECURE", "false").lower() == "true"

# S3A Configuration for Spark
S3A_ENDPOINT = f"http://{MINIO_ENDPOINT}"
S3A_ACCESS_KEY = MINIO_ACCESS_KEY
S3A_SECRET_KEY = MINIO_SECRET_KEY


def get_spark_session(app_name: str = "DataPlatformSpark") -> SparkSession:
    """Create and configure Spark session for MinIO/S3A access."""
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .config("spark.hadoop.fs.s3a.endpoint", S3A_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", S3A_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", S3A_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", str(MINIO_SECURE).lower())
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")
        .getOrCreate()
    )


def get_sales_schema() -> StructType:
    """Define the schema for sales data."""
    return StructType([
        StructField("transaction_id", StringType(), False),
        StructField("transaction_date", DateType(), False),
        StructField("customer_id", StringType(), False),
        StructField("product_id", StringType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("unit_price", DecimalType(12, 2), False),
    ])


def bronze_to_silver(spark: SparkSession, bronze_path: str, silver_path: str):
    """
    Transform bronze data to silver:
    - Remove duplicates
    - Validate data quality
    - Add calculated fields
    """
    logger.info(f"Reading bronze data from {bronze_path}")
    df = spark.read.schema(get_sales_schema()).csv(bronze_path, header=True)

    initial_count = df.count()
    logger.info(f"Bronze records: {initial_count}")

    # Remove duplicates on transaction_id
    df = df.dropDuplicates(["transaction_id"])
    after_dedup = df.count()
    logger.info(f"After deduplication: {after_dedup} (removed {initial_count - after_dedup} duplicates)")

    # Filter valid records
    df = df.filter((col("quantity") > 0) & (col("unit_price") >= 0))
    after_valid = df.count()
    logger.info(f"After validation: {after_valid} (removed {after_dedup - after_valid} invalid)")

    # Add total_amount column
    df = df.withColumn("total_amount", col("quantity") * col("unit_price"))

    logger.info(f"Writing silver data to {silver_path}")
    df.write.mode("overwrite").option("header", "true").csv(silver_path)

    logger.info(f"Silver transformation complete: {after_valid} records")
    return df


def silver_to_gold(spark: SparkSession, silver_path: str, gold_path: str):
    """
    Aggregate silver data to gold daily summary.
    """
    logger.info(f"Reading silver data from {silver_path}")
    df = spark.read.option("header", "true").csv(silver_path)

    # Ensure proper types
    df = df.withColumn("transaction_date", to_date(col("transaction_date")))
    df = df.withColumn("quantity", col("quantity").cast(IntegerType()))
    df = df.withColumn("total_amount", col("total_amount").cast(DecimalType(14, 2)))

    # Aggregate by date
    gold_df = df.groupBy("transaction_date").agg(
        count("*").alias("transaction_count"),
        spark_sum("quantity").alias("units_sold"),
        spark_sum("total_amount").alias("revenue"),
    ).orderBy("transaction_date")

    count = gold_df.count()
    logger.info(f"Gold records: {count}")

    logger.info(f"Writing gold data to {gold_path}")
    gold_df.write.mode("overwrite").option("header", "true").csv(gold_path)

    logger.info("Gold aggregation complete")
    return gold_df


def run_full_pipeline():
    """Run the complete Spark pipeline: bronze -> silver -> gold."""
    spark = get_spark_session("DataPlatformFullPipeline")

    try:
        bronze_path = "s3a://bronze/sales/"
        silver_path = "s3a://silver/sales/"
        gold_path = "s3a://gold/sales_daily/"

        # Bronze to Silver
        silver_df = bronze_to_silver(spark, bronze_path, silver_path)

        # Silver to Gold
        gold_df = silver_to_gold(spark, silver_path, gold_path)

        logger.info("Full Spark pipeline completed successfully!")

    finally:
        spark.stop()


def run_silver_only():
    """Run only bronze to silver transformation."""
    spark = get_spark_session("DataPlatformSilverOnly")

    try:
        bronze_path = "s3a://bronze/sales/"
        silver_path = "s3a://silver/sales/"

        bronze_to_silver(spark, bronze_path, silver_path)

    finally:
        spark.stop()


def run_gold_only():
    """Run only silver to gold aggregation."""
    spark = get_spark_session("DataPlatformGoldOnly")

    try:
        silver_path = "s3a://silver/sales/"
        gold_path = "s3a://gold/sales_daily/"

        silver_to_gold(spark, silver_path, gold_path)

    finally:
        spark.stop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "silver":
            run_silver_only()
        elif sys.argv[1] == "gold":
            run_gold_only()
        else:
            run_full_pipeline()
    else:
        run_full_pipeline()