# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Main Data Platform Pipeline DAG.

This DAG orchestrates the complete data pipeline:
1. Ingestion: Load raw data from CSV to PostgreSQL (raw schema) and MinIO (bronze)
2. Transformation: Clean and transform bronze -> silver -> gold (MinIO + PostgreSQL)
3. Staging: Load silver data to PostgreSQL staging schema
4. Marts: Build business-ready mart tables
5. Quality: Run data quality checks at each layer
6. Gold: Create aggregated gold layer tables
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Import lineage tracking
import sys
sys.path.append('/opt/airflow/project')
from ingestion.lineage import track_ingestion, track_transformation, track_quality_check


PROJECT_DIR = "/opt/airflow/project"
PG_CONN = "-h datawarehouse -U dataeng -d datawarehouse"
PG_ENV = {"PGPASSWORD": "dataeng"}


def emit_ingestion_lineage(**context):
    """Emit lineage event for ingestion step."""
    run_id = context['run_id']
    track_ingestion(
        source_name="sales.csv",
        target_table="raw.sales",
        run_id=run_id,
        row_count=10,  # Sample data has 10 rows
    )


def emit_silver_lineage(**context):
    """Emit lineage event for silver transformation."""
    run_id = context['run_id']
    track_transformation(
        job_name="silver_transformation",
        input_tables=["raw.sales"],
        output_table="silver.sales_clean",
        sql_query="""
            SELECT DISTINCT ON (transaction_id) *,
                   quantity * unit_price AS total_amount
            FROM raw.sales
            WHERE quantity > 0 AND unit_price >= 0
        """,
        run_id=run_id,
    )


def emit_gold_lineage(**context):
    """Emit lineage event for gold aggregation."""
    run_id = context['run_id']
    track_transformation(
        job_name="gold_aggregation",
        input_tables=["silver.sales_clean"],
        output_table="mart.sales_daily",
        sql_query="""
            SELECT transaction_date,
                   COUNT(*) AS transaction_count,
                   SUM(quantity) AS units_sold,
                   SUM(total_amount) AS revenue
            FROM silver.sales_clean
            GROUP BY transaction_date
            ORDER BY transaction_date
        """,
        run_id=run_id,
    )


def emit_quality_lineage(**context):
    """Emit lineage event for quality checks."""
    run_id = context['run_id']
    track_quality_check(
        table_name="mart.sales",
        checks=["unique_transaction_id", "positive_quantity", "positive_price", "not_null_customer"],
        passed=True,
        run_id=run_id,
    )


with DAG(
    dag_id="data_platform_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-platform", "medallion"],
    default_args={
        "owner": "data-engineering",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": False,
    },
    doc_md=__doc__,
) as dag:

    # Task 1: Create MinIO buckets (idempotent)
    init_minio = BashOperator(
        task_id="init_minio",
        bash_command=(
            "mc alias set myminio http://minio:9000 minioadmin minioadmin && "
            "mc mb --ignore-existing myminio/bronze && "
            "mc mb --ignore-existing myminio/silver && "
            "mc mb --ignore-existing myminio/gold"
        ),
    )

    # Task 2: Initialize database schemas
    init_schema = BashOperator(
        task_id="init_schema",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/init_schema.sql"
        ),
        env=PG_ENV,
    )

    # Task 3: Ingestion - CSV to PostgreSQL raw + MinIO bronze
    ingestion = BashOperator(
        task_id="ingestion",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python ingestion/sales_pipeline_minio.py"
        ),
    )

    # Task 4: Emit ingestion lineage
    ingestion_lineage = PythonOperator(
        task_id="ingestion_lineage",
        python_callable=emit_ingestion_lineage,
        provide_context=True,
    )

    # Task 5: Silver transformation - Bronze to Silver (MinIO)
    silver = BashOperator(
        task_id="silver",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python transformation/sales_silver_minio.py"
        ),
    )

    # Task 6: Emit silver lineage
    silver_lineage = PythonOperator(
        task_id="silver_lineage",
        python_callable=emit_silver_lineage,
        provide_context=True,
    )

    # Task 7: Load silver to PostgreSQL staging
    load_staging = BashOperator(
        task_id="load_staging",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/staging/sales.sql"
        ),
        env=PG_ENV,
    )

    # Task 8: Build marts
    build_marts = BashOperator(
        task_id="build_marts",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/marts/sales.sql"
        ),
        env=PG_ENV,
    )

    # Task 9: Data quality checks on mart layer
    quality = BashOperator(
        task_id="quality",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python quality/sales_quality.py"
        ),
    )

    # Task 10: Emit quality lineage
    quality_lineage = PythonOperator(
        task_id="quality_lineage",
        python_callable=emit_quality_lineage,
        provide_context=True,
    )

    # Task 11: Build gold layer (daily aggregation)
    gold = BashOperator(
        task_id="gold",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/gold_sales.sql"
        ),
        env=PG_ENV,
    )

    # Task 12: Emit gold lineage
    gold_lineage = PythonOperator(
        task_id="gold_lineage",
        python_callable=emit_gold_lineage,
        provide_context=True,
    )

    # Task 13: Gold quality checks
    gold_quality = BashOperator(
        task_id="gold_quality",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python quality/gold_quality.py"
        ),
    )

    # Task dependencies
    (
        init_minio
        >> init_schema
        >> ingestion
        >> ingestion_lineage
        >> silver
        >> silver_lineage
        >> load_staging
        >> build_marts
        >> quality
        >> quality_lineage
        >> gold
        >> gold_lineage
        >> gold_quality
    )