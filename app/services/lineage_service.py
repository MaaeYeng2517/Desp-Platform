import os
import uuid as uuid_module
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.core.config import settings

try:
    from openlineage.client import OpenLineageClient
    from openlineage.client.facet import (
        SchemaDatasetFacet,
        SchemaField,
        SQLJobFacet,
        ErrorMessageRunFacet,
    )
    from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
    OPENLINEAGE_AVAILABLE = True
except ImportError:
    OPENLINEAGE_AVAILABLE = False
    OpenLineageClient = None


_LINEAGE_EVENTS: List[Dict[str, Any]] = []


class LineageService:
    """
    Service for tracking data lineage using OpenLineage.

    Emits START, COMPLETE, and FAIL events for data operations,
    enabling end-to-end lineage tracking across the Data Core Platform.
    """

    def __init__(self):
        self.endpoint = settings.OPENLINEAGE_ENDPOINT if hasattr(settings, "OPENLINEAGE_ENDPOINT") else os.getenv("OPENLINEAGE_ENDPOINT", "http://localhost:5000")
        self.api_key = os.getenv("OPENLINEAGE_API_KEY")
        self.namespace = os.getenv("OPENLINEAGE_NAMESPACE", "data-core-platform")
        self.producer = "https://github.com/MaaeYEng2517/data-engineering-platform"
        self.client = None

        if OPENLINEAGE_AVAILABLE:
            try:
                kwargs = {"url": self.endpoint}
                if self.api_key:
                    kwargs["headers"] = {"Authorization": f"Bearer {self.api_key}"}
                self.client = OpenLineageClient(**kwargs)
            except Exception as e:
                print(f"Warning: Could not initialize OpenLineage client: {e}")

    def emit_event(
        self,
        event_type: str,
        job_name: str,
        run_id: Optional[str] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
        job_facets: Optional[Dict[str, Any]] = None,
        run_facets: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> str:
        run_id = run_id or str(uuid_module.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"

        event_record = {
            "eventType": event_type,
            "eventTime": timestamp,
            "run": {"runId": run_id, "facets": run_facets or {}},
            "job": {"namespace": self.namespace, "name": job_name, "facets": job_facets or {}},
            "inputs": inputs or [],
            "outputs": outputs or [],
            "producer": self.producer,
            "eventTime": timestamp,
        }

        if error_message and event_type == "FAIL":
            event_record["run"]["facets"]["errorMessage"] = {
                "message": error_message,
                "programmingLanguage": "PYTHON",
            }

        _LINEAGE_EVENTS.append(event_record)

        if self.client:
            try:
                run = Run(runId=run_id)
                job = Job(namespace=self.namespace, name=job_name)

                ol_inputs = [
                    Dataset(
                        namespace=self.namespace,
                        name=d.get("name", ""),
                        facets=d.get("facets", {}),
                    )
                    for d in inputs or []
                ]
                ol_outputs = [
                    Dataset(
                        namespace=self.namespace,
                        name=d.get("name", ""),
                        facets=d.get("facets", {}),
                    )
                    for d in outputs or []
                ]

                event = RunEvent(
                    eventType=getattr(RunState, event_type),
                    eventTime=timestamp,
                    run=run,
                    job=job,
                    producer=self.producer,
                    inputs=ol_inputs,
                    outputs=ol_outputs,
                    jobFacets=job_facets or {},
                    runFacets=run_facets or {},
                )
                self.client.emit(event)
            except Exception as e:
                print(f"Warning: Failed to emit lineage event: {e}")

        return run_id

    def emit_start(
        self,
        job_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
        run_id: Optional[str] = None,
        job_facets: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.emit_event("START", job_name, run_id, inputs, outputs, job_facets)

    def emit_complete(
        self,
        job_name: str,
        run_id: str,
        outputs: Optional[List[Dict[str, Any]]] = None,
        run_facets: Optional[Dict[str, Any]] = None,
    ):
        self.emit_event("COMPLETE", job_name, run_id, None, outputs, None, run_facets)

    def emit_fail(
        self,
        job_name: str,
        run_id: str,
        error_message: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
    ):
        self.emit_event("FAIL", job_name, run_id, inputs, None, None, None, error_message)

    def track_ingestion(
        self,
        source_name: str,
        target_table: str,
        run_id: Optional[str] = None,
        row_count: Optional[int] = None,
    ) -> str:
        inputs = [{"name": f"{self.namespace}.{source_name}"}]
        outputs = [{"name": f"{self.namespace}.{target_table}"}]
        job_facets = {}
        if row_count:
            job_facets["rowCount"] = {"rowCount": row_count}
        return self.emit_start("ingestion", inputs, outputs, run_id, job_facets)

    def track_transformation(
        self,
        job_name: str,
        input_tables: List[str],
        output_table: str,
        sql_query: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        inputs = [{"name": f"{self.namespace}.{t}"} for t in input_tables]
        outputs = [{"name": f"{self.namespace}.{output_table}"}]
        job_facets = {}
        if sql_query:
            job_facets["sql"] = sql_query
        return self.emit_start(job_name, inputs, outputs, run_id, job_facets)

    def track_quality_check(
        self,
        table_name: str,
        checks: List[str],
        passed: bool,
        run_id: Optional[str] = None,
    ):
        inputs = [{"name": f"{self.namespace}.{table_name}"}]
        if passed:
            self.emit_complete("quality_check", run_id or str(uuid_module.uuid4()), None, None)
        else:
            self.emit_fail(
                "quality_check",
                run_id or str(uuid_module.uuid4()),
                f"Quality checks failed: {', '.join(checks)}",
                inputs,
            )

    def get_events(self) -> List[Dict[str, Any]]:
        return list(_LINEAGE_EVENTS)

    def get_events_by_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        return [e for e in _LINEAGE_EVENTS if e.get("job", {}).get("namespace") == namespace]

    def clear_events(self):
        _LINEAGE_EVENTS.clear()


lineage_service = LineageService()
