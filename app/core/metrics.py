import os
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_PROMETHEUS
from starlette.responses import Response


PIPELINE_RUNS = Counter(
    "data_core_pipeline_runs_total",
    "Total number of pipeline runs",
    ["pipeline", "status"],
)

FILES_PROCESSED = Counter(
    "data_core_files_processed_total",
    "Total files processed",
    ["operation", "status"],
)

RECORDS_PROCESSED = Counter(
    "data_core_records_processed_total",
    "Total records processed",
    ["layer"],
)

QUALITY_CHECKS = Counter(
    "data_core_quality_checks_total",
    "Quality check results",
    ["status"],
)

API_REQUESTS = Counter(
    "data_core_api_requests_total",
    "API request count",
    ["method", "endpoint", "status_code"],
)

DATASET_COUNT = Gauge(
    "data_core_datasets_total",
    "Number of registered datasets",
)

PIPELINE_LATENCY = Histogram(
    "data_core_pipeline_latency_seconds",
    "Pipeline execution latency",
    ["pipeline"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1200],
)

UPLOAD_SIZE = Histogram(
    "data_core_upload_size_bytes",
    "Distribution of uploaded file sizes",
    buckets=[100, 1000, 10000, 100000, 1000000, 10000000, 100000000],
)


def metrics_endpoint(request):
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_PROMETHEUS,
    )


def update_dataset_gauge(count: int):
    DATASET_COUNT.set(count)


def record_api_request(method: str, endpoint: str, status_code: int):
    API_REQUESTS.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
