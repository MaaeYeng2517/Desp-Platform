# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Integration tests for the full data pipeline.

These tests require a running PostgreSQL and MinIO instance.
Run with: pytest tests/integration/ -v
"""

import pytest
import pandas as pd
import os
from sqlalchemy import create_engine, text
from minio import Minio

# Test configuration
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = int(os.getenv("TEST_DB_PORT", "5432"))
TEST_DB_USER = os.getenv("TEST_DB_USER", "dataeng")
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "dataeng")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "datawarehouse")

TEST_MINIO_ENDPOINT = os.getenv("TEST_MINIO_ENDPOINT", "localhost:9000")
TEST_MINIO_ACCESS_KEY = os.getenv("TEST_MINIO_ACCESS_KEY", "minioadmin")
TEST_MINIO_SECRET_KEY = os.getenv("TEST_MINIO_SECRET_KEY", "minioadmin")
TEST_MINIO_SECURE = os.getenv("TEST_MINIO_SECURE", "false").lower() == "true"

DATABASE_URL = f"postgresql+psycopg2://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for tests."""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def minio_client():
    """Create MinIO client for tests."""
    client = Minio(
        endpoint=TEST_MINIO_ENDPOINT,
        access_key=TEST_MINIO_ACCESS_KEY,
        secret_key=TEST_MINIO_SECRET_KEY,
        secure=TEST_MINIO_SECURE,
    )
    yield client


@pytest.fixture(scope="function")
def clean_database(db_engine):
    """Clean database before each test."""
    with db_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS raw.sales CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS staging.sales CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS mart.sales CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS mart.sales_daily CASCADE"))
        conn.commit()

    # Recreate schemas
    with db_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS mart"))
        conn.commit()


@pytest.fixture(scope="function")
def clean_minio(minio_client):
    """Clean MinIO buckets before each test."""
    for bucket in ["bronze", "silver", "gold"]:
        if minio_client.bucket_exists(bucket):
            objects = minio_client.list_objects(bucket, recursive=True)
            for obj in objects:
                minio_client.remove_object(bucket, obj.object_name)
    yield


class TestFullPipelineIntegration:
    """Integration tests for the complete pipeline."""

    def test_ingestion_pipeline(self, db_engine, minio_client, clean_database, clean_minio):
        """Test ingestion from CSV to PostgreSQL and MinIO."""
        from ingestion.sales_pipeline_minio import main

        # Set environment variables
        os.environ["PGPASSWORD"] = TEST_DB_PASSWORD
        os.environ["DB_HOST"] = TEST_DB_HOST
        os.environ["MINIO_ENDPOINT"] = TEST_MINIO_ENDPOINT
        os.environ["MINIO_ACCESS_KEY"] = TEST_MINIO_ACCESS_KEY
        os.environ["MINIO_SECRET_KEY"] = TEST_MINIO_SECRET_KEY
        os.environ["MINIO_SECURE"] = str(TEST_MINIO_SECURE).lower()

        # Run ingestion
        main()

        # Verify PostgreSQL
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM raw.sales")).scalar()
            assert result == 10  # Sample data has 10 rows

            # Check columns
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'raw' AND table_name = 'sales'
                ORDER BY ordinal_position
            """)).fetchall()
            columns = [r[0] for r in result]
            expected = ["transaction_id", "transaction_date", "customer_id", "product_id", "quantity", "unit_price", "loaded_at"]
            assert columns == expected

        # Verify MinIO
        objects = list(minio_client.list_objects("bronze", recursive=True))
        assert len(objects) == 1
        assert objects[0].object_name == "sales/sales.csv"

    def test_transformation_pipeline(self, db_engine, minio_client, clean_database, clean_minio):
        """Test bronze to silver to gold transformation."""
        from ingestion.sales_pipeline_minio import main as run_ingestion
        from transformation.sales_silver_minio import transform

        # First run ingestion to populate bronze
        os.environ["PGPASSWORD"] = TEST_DB_PASSWORD
        os.environ["DB_HOST"] = TEST_DB_HOST
        os.environ["MINIO_ENDPOINT"] = TEST_MINIO_ENDPOINT
        os.environ["MINIO_ACCESS_KEY"] = TEST_MINIO_ACCESS_KEY
        os.environ["MINIO_SECRET_KEY"] = TEST_MINIO_SECRET_KEY
        os.environ["MINIO_SECURE"] = str(TEST_MINIO_SECURE).lower()

        run_ingestion()

        # Run transformation
        transform()

        # Verify MinIO silver
        silver_objects = list(minio_client.list_objects("silver", recursive=True))
        assert len(silver_objects) == 1
        assert silver_objects[0].object_name == "sales/sales_clean.csv"

        # Verify MinIO gold
        gold_objects = list(minio_client.list_objects("gold", recursive=True))
        assert len(gold_objects) == 1
        assert gold_objects[0].object_name == "sales/sales_daily.csv"

        # Verify gold data content
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            minio_client.fget_object("gold", "sales/sales_daily.csv", tmp.name)
            gold_df = pd.read_csv(tmp.name)

        assert len(gold_df) > 0
        assert "transaction_date" in gold_df.columns
        assert "transaction_count" in gold_df.columns
        assert "units_sold" in gold_df.columns
        assert "revenue" in gold_df.columns

    def test_staging_load(self, db_engine, minio_client, clean_database, clean_minio):
        """Test loading silver data to PostgreSQL staging."""
        from ingestion.sales_pipeline_minio import main as run_ingestion
        from transformation.sales_silver_minio import transform

        os.environ["PGPASSWORD"] = TEST_DB_PASSWORD
        os.environ["DB_HOST"] = TEST_DB_HOST
        os.environ["MINIO_ENDPOINT"] = TEST_MINIO_ENDPOINT
        os.environ["MINIO_ACCESS_KEY"] = TEST_MINIO_ACCESS_KEY
        os.environ["MINIO_SECRET_KEY"] = TEST_MINIO_SECRET_KEY
        os.environ["MINIO_SECURE"] = str(TEST_MINIO_SECURE).lower()

        run_ingestion()
        transform()

        # Load staging
        with db_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO staging.sales
                SELECT transaction_id, transaction_date, customer_id, product_id,
                       quantity, unit_price, quantity * unit_price as total_amount
                FROM (
                    SELECT * FROM (
                        SELECT *,
                               ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_id) as rn
                        FROM (
                            SELECT * FROM raw.sales
                        ) t
                    ) t WHERE rn = 1
                ) t
                WHERE quantity > 0 AND unit_price >= 0
            """))
            conn.commit()

        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM staging.sales")).scalar()
            assert result > 0

    def test_mart_build(self, db_engine, minio_client, clean_database, clean_minio):
        """Test building mart tables from staging."""
        from ingestion.sales_pipeline_minio import main as run_ingestion
        from transformation.sales_silver_minio import transform

        os.environ["PGPASSWORD"] = TEST_DB_PASSWORD
        os.environ["DB_HOST"] = TEST_DB_HOST
        os.environ["MINIO_ENDPOINT"] = TEST_MINIO_ENDPOINT
        os.environ["MINIO_ACCESS_KEY"] = TEST_MINIO_ACCESS_KEY
        os.environ["MINIO_SECRET_KEY"] = TEST_MINIO_SECRET_KEY
        os.environ["MINIO_SECURE"] = str(TEST_MINIO_SECURE).lower()

        run_ingestion()
        transform()

        # Load staging
        with db_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO staging.sales
                SELECT transaction_id, transaction_date, customer_id, product_id,
                       quantity, unit_price, quantity * unit_price as total_amount
                FROM (
                    SELECT * FROM (
                        SELECT *,
                               ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_id) as rn
                        FROM raw.sales
                    ) t WHERE rn = 1
                ) t
                WHERE quantity > 0 AND unit_price >= 0
            """))
            conn.commit()

        # Build mart
        with db_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO mart.sales
                SELECT transaction_id, transaction_date, customer_id, product_id,
                       quantity, unit_price, total_amount
                FROM staging.sales
            """))
            conn.commit()

        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM mart.sales")).scalar()
            assert result > 0

    def test_quality_checks_pass(self, db_engine, minio_client, clean_database, clean_minio):
        """Test quality checks pass with valid data."""
        from ingestion.sales_pipeline_minio import main as run_ingestion
        from transformation.sales_silver_minio import transform
        from quality.sales_quality import check_quality
        from quality.gold_quality import run_quality as run_gold_quality

        os.environ["PGPASSWORD"] = TEST_DB_PASSWORD
        os.environ["DB_HOST"] = TEST_DB_HOST
        os.environ["MINIO_ENDPOINT"] = TEST_MINIO_ENDPOINT
        os.environ["MINIO_ACCESS_KEY"] = TEST_MINIO_ACCESS_KEY
        os.environ["MINIO_SECRET_KEY"] = TEST_MINIO_SECRET_KEY
        os.environ["MINIO_SECURE"] = str(TEST_MINIO_SECURE).lower()

        run_ingestion()
        transform()

        # Load staging and mart
        with db_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO staging.sales
                SELECT transaction_id, transaction_date, customer_id, product_id,
                       quantity, unit_price, quantity * unit_price as total_amount
                FROM (
                    SELECT * FROM (
                        SELECT *,
                               ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_id) as rn
                        FROM raw.sales
                    ) t WHERE rn = 1
                ) t
                WHERE quantity > 0 AND unit_price >= 0
            """))
            conn.execute(text("""
                INSERT INTO mart.sales
                SELECT transaction_id, transaction_date, customer_id, product_id,
                       quantity, unit_price, total_amount
                FROM staging.sales
            """))
            conn.commit()

        # Run quality checks - should not raise
        check_quality()

        # Build gold
        with db_engine.connect() as conn:
            conn.execute(text("""
                DROP TABLE IF EXISTS mart.sales_daily;
                CREATE TABLE mart.sales_daily AS
                SELECT transaction_date,
                       COUNT(*) AS transaction_count,
                       SUM(quantity) AS units_sold,
                       SUM(total_amount) AS revenue
                FROM staging.sales
                GROUP BY transaction_date
                ORDER BY transaction_date
            """))
            conn.commit()

        # Run gold quality checks - should not raise
        run_gold_quality()

    def test_data_lineage_tracking(self, db_engine, minio_client, clean_database, clean_minio):
        """Test lineage tracking emits events."""
        from ingestion.lineage import track_ingestion, track_transformation, track_quality_check

        run_id = "test-run-123"

        # These should not raise even if OpenLineage backend is not available
        track_ingestion("sales.csv", "raw.sales", run_id, 10)
        track_transformation("silver", ["raw.sales"], "silver.sales_clean", "SELECT ...", run_id)
        track_quality_check("mart.sales", ["unique_id", "positive_qty"], True, run_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])