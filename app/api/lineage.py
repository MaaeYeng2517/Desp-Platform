from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.services.lineage_service import lineage_service

router = APIRouter(
    prefix="/lineage",
    tags=["Data Lineage (OpenLineage)"],
)


@router.get("/events")
async def get_lineage_events(
    limit: int = 100,
    namespace: Optional[str] = Query(None, description="Filter by OpenLineage namespace"),
):
    events = lineage_service.get_events() if not namespace else lineage_service.get_events_by_namespace(namespace)
    return {"events": events[-limit:]}


@router.get("/events/{run_id}")
async def get_lineage_event(run_id: str):
    events = lineage_service.get_events()
    for e in events:
        if e.get("run", {}).get("runId") == run_id:
            return {"event": e}
    raise HTTPException(status_code=404, detail=f"Run {run_id} not found")


@router.post("/clear")
async def clear_lineage_events():
    lineage_service.clear_events()
    return {"message": "Lineage events cleared"}


@router.post("/track/ingestion")
async def track_ingestion(
    source_name: str,
    target_table: str,
    row_count: Optional[int] = None,
):
    run_id = lineage_service.track_ingestion(source_name, target_table, row_count=row_count)
    return {"run_id": run_id, "message": "Ingestion lineage event emitted"}


@router.post("/track/transformation")
async def track_transformation(
    job_name: str,
    input_tables: List[str],
    output_table: str,
    sql_query: Optional[str] = None,
):
    run_id = lineage_service.track_transformation(job_name, input_tables, output_table, sql_query=sql_query)
    return {"run_id": run_id, "message": "Transformation lineage event emitted"}


@router.post("/track/quality")
async def track_quality(
    table_name: str,
    checks: List[str],
    passed: bool,
):
    run_id = str(__import__("uuid").uuid4())
    lineage_service.track_quality_check(table_name, checks, passed, run_id=run_id)
    return {"run_id": run_id, "message": "Quality check lineage event emitted"}


@router.get("/status")
async def lineage_status():
    events = lineage_service.get_events()
    return {
        "openlineage_available": lineage_service.client is not None,
        "namespace": lineage_service.namespace,
        "endpoint": lineage_service.endpoint,
        "total_events": len(events),
        "recent_events": events[-20:] if len(events) > 20 else events,
    }
