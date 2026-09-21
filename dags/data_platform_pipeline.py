from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="data_platform_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["data-platform"],
) as dag:

    bronze = BashOperator(
        task_id="bronze",
        bash_command="""
        mkdir -p data/bronze/sales
        cp data/raw/sales.csv \
           data/bronze/sales/sales.csv
        """
    )

    silver = BashOperator(
        task_id="silver",
        bash_command="""
        python transformation/sales_silver.py
        """
    )

    quality = BashOperator(
        task_id="quality",
        bash_command="""
        python quality/sales_quality.py
        """
    )

    gold = BashOperator(
        task_id="gold",
        bash_command="""
        psql \
          -h postgres \
          -U dataeng \
          -d datawarehouse \
          -f sql/gold_sales.sql
        """,
        env={
            "PGPASSWORD": "dataeng"
        }
    )

    gold_quality = BashOperator(
        task_id="gold_quality",
        bash_command="""
        python quality/gold_quality.py
        """
    )

