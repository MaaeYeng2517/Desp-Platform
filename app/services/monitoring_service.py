from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

from app.core.metrics import (
    PIPELINE_RUNS,
    PIPELINE_LATENCY,
    FILES_PROCESSED,
    RECORDS_PROCESSED,
    QUALITY_CHECKS,
    update_dataset_gauge,
)


class MonitoringState:
    _lock = threading.Lock()
    _pipeline_runs: Dict[str, Dict[str, Any]] = {}
    _dataset_count: int = 0
    _quality_summary: Dict[str, int] = {"pass": 0, "fail": 0, "warning": 0}

    @classmethod
    def record_pipeline_run(cls, name: str, status: str, latency: float, records: int = 0, errors: int = 0):
        with cls._lock:
            PIPELINE_RUNS.labels(pipeline=name, status=status).inc()
            if latency:
                PIPELINE_LATENCY.labels(pipeline=name).observe(latency)
            if records:
                RECORDS_PROCESSED.labels(layer=name).inc(records)
            cls._pipeline_runs[name] = {
                "last_status": status,
                "last_run": datetime.utcnow().isoformat(),
                "last_latency": latency,
                "total_records": records,
                "total_errors": errors,
            }

    @classmethod
    def record_file_processed(cls, operation: str, status: str, records: int = 0):
        with cls._lock:
            FILES_PROCESSED.labels(operation=operation, status=status).inc()
            if records:
                RECORDS_PROCESSED.labels(layer=operation).inc(records)

    @classmethod
    def record_quality_result(cls, status: str):
        with cls._lock:
            QUALITY_CHECKS.labels(status=status).inc()
            if status in cls._quality_summary:
                cls._quality_summary[status] += 1

    @classmethod
    def record_validation_result(cls, status: str, record_count: int = 0):
        with cls._lock:
            cls._dataset_count = cls._dataset_count

    @classmethod
    def set_dataset_count(cls, count: int):
        with cls._lock:
            cls._dataset_count = count
            update_dataset_gauge(count)

    @classmethod
    def get_pipeline_runs(cls) -> Dict[str, Dict[str, Any]]:
        with cls._lock:
            return dict(cls._pipeline_runs)

    @classmethod
    def get_dataset_count(cls) -> int:
        with cls._lock:
            return cls._dataset_count

    @classmethod
    def get_quality_summary(cls) -> Dict[str, int]:
        with cls._lock:
            return dict(cls._quality_summary)

    @classmethod
    def get_overall_status(cls) -> Dict[str, Any]:
        with cls._lock:
            runs = dict(cls._pipeline_runs)
            active = sum(1 for r in runs.values() if r["last_status"] in ("running", "started"))
            failed = sum(1 for r in runs.values() if r["last_status"] == "failed")
            last_error_rate = 0.0
            if active > 0:
                last_error_rate = failed / active if active > 0 else 0.0

            return {
                "datasets_registered": cls._dataset_count,
                "active_pipelines": active,
                "failed_pipelines": failed,
                "last_error_rate": round(last_error_rate, 2),
                "quality_summary": dict(cls._quality_summary),
            }
