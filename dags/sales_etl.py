from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="sales_etl_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-engineering", "etl"],
) as dag:

    extract_load = BashOperator(
        task_id="extract_load",
        bash_command=(
            "cd /opt/airflow/project && "
            "python ingestion/sales_pipeline.py"
        ),
    )

    transform = BashOperator(
        task_id="transform",
        bash_command=(
            "cd /opt/airflow/project && "
            "psql "
            "-h postgres "
            "-U dataeng "
            "-d datawarehouse "
            "-f sql/staging/sales.sql"
        ),
        env={
            "PGPASSWORD": "dataeng"
        },
    )

    quality = BashOperator(
        task_id="quality",
        bash_command=(
            "cd /opt/airflow/project && "
            "python quality/sales_quality.py"
        ),
    )

    mart = BashOperator(
        task_id="build_mart",
        bash_command=(
            "cd /opt/airflow/project && "
            "psql "
            "-h postgres "
            "-U dataeng "
            "-d datawarehouse "
            "-f sql/marts/sales.sql"
        ),
        env={
            "PGPASSWORD": "dataeng"
        },
    )

    extract_load >> transform >> quality >> mart
