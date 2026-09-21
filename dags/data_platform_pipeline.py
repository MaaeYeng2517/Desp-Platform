from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"
PG_CONN = "-h postgres -U dataeng -d datawarehouse"
PG_ENV = {"PGPASSWORD": "dataeng"}


with DAG(
    dag_id="data_platform_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-platform"],
) as dag:

    bronze = BashOperator(
        task_id="bronze",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "mkdir -p data/bronze/sales && "
            "cp data/raw/sales.csv data/bronze/sales/sales.csv"
        ),
    )

    silver = BashOperator(
        task_id="silver",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python transformation/sales_silver.py"
        ),
    )

    init_schema = BashOperator(
        task_id="init_schema",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/init_schema.sql"
        ),
        env=PG_ENV,
    )

    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python ingestion/sales_pipeline.py"
        ),
    )

    staging = BashOperator(
        task_id="staging",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/staging/sales.sql"
        ),
        env=PG_ENV,
    )

    mart = BashOperator(
        task_id="mart",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/marts/sales.sql"
        ),
        env=PG_ENV,
    )

    quality = BashOperator(
        task_id="quality",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python quality/sales_quality.py"
        ),
    )

    gold = BashOperator(
        task_id="gold",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            f"psql {PG_CONN} -f sql/gold_sales.sql"
        ),
        env=PG_ENV,
    )

    gold_quality = BashOperator(
        task_id="gold_quality",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python quality/gold_quality.py"
        ),
    )

    (
        bronze
        >> silver
        >> init_schema
        >> load_raw
        >> staging
        >> mart
        >> quality
        >> gold
        >> gold_quality
    )
