#!/bin/bash
# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

# Spark Job Submit Script for Airflow
# Usage: ./submit_spark_job.sh [silver|gold|full]

set -e

SPARK_MASTER="spark://spark-master:7077"
JOB_TYPE="${1:-full}"
PROJECT_DIR="/opt/airflow/project"

echo "Submitting Spark job: $JOB_TYPE"

case $JOB_TYPE in
    silver)
        spark-submit \
            --master "$SPARK_MASTER" \
            --deploy-mode cluster \
            --name "DataPlatform-Silver" \
            --conf spark.sql.adaptive.enabled=true \
            --conf spark.sql.adaptive.coalescePartitions.enabled=true \
            --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
            "$PROJECT_DIR/transformation/spark_transform.py" silver
        ;;
    gold)
        spark-submit \
            --master "$SPARK_MASTER" \
            --deploy-mode cluster \
            --name "DataPlatform-Gold" \
            --conf spark.sql.adaptive.enabled=true \
            --conf spark.sql.adaptive.coalescePartitions.enabled=true \
            --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
            "$PROJECT_DIR/transformation/spark_transform.py" gold
        ;;
    full|*)
        spark-submit \
            --master "$SPARK_MASTER" \
            --deploy-mode cluster \
            --name "DataPlatform-FullPipeline" \
            --conf spark.sql.adaptive.enabled=true \
            --conf spark.sql.adaptive.coalescePartitions.enabled=true \
            --packages org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 \
            "$PROJECT_DIR/transformation/spark_transform.py"
        ;;
esac

echo "Spark job submitted successfully"