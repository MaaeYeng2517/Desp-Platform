# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def extract():
    print("Extract data")


def transform():
    print("Transform data")


def load():
    print("Load data")


with DAG(
    dag_id="hello_data_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )

