import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.core.metrics import metrics_endpoint
from app.services.monitoring_service import MonitoringState

router = APIRouter(
    prefix="/monitor",
    tags=["Monitor"],
)


@router.get("/metrics")
async def prometheus_metrics():
    return metrics_endpoint(None)


@router.get("/status")
async def get_overall_status():
    return MonitoringState.get_overall_status()


@router.get("/pipeline/runs")
async def get_pipeline_runs():
    return {
        "pipelines": MonitoringState.get_pipeline_runs(),
        "datasets": MonitoringState.get_dataset_count(),
    }


@router.post("/pipeline/run/{pipeline_name}")
async def trigger_pipeline(
    pipeline_name: str,
    current_user: str = "system",
):
    start = time.time()
    MonitoringState.record_pipeline_run(pipeline_name, "started", 0)

    try:
        result = {
            "pipeline": pipeline_name,
            "status": "triggered",
            "triggered_by": current_user,
            "started_at": datetime.utcnow().isoformat(),
        }
        return result
    except Exception as e:
        elapsed = time.time() - start
        MonitoringState.record_pipeline_run(pipeline_name, "failed", elapsed)
        raise HTTPException(status_code=500, detail=str(e))
