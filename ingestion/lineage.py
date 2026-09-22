# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
OpenLineage integration for data lineage tracking.

This module provides utilities to emit lineage events from Python operators
and SQL transformations to an OpenLineage-compatible backend (e.g., Marquez, DataHub).
"""

import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

try:
    from openlineage.client import OpenLineageClient
    from openlineage.client.facet import (
        DataSourceDatasetFacet,
        SchemaDatasetFacet,
        SchemaField,
        SQLJobFacet,
        ErrorMessageRunFacet,
        ExtractionErrorRunFacet,
    )
    from openlineage.client.run import RunEvent, RunState, Run, Job, Dataset
    OPENLINEAGE_AVAILABLE = True
except ImportError:
    OPENLINEAGE_AVAILABLE = False
    OpenLineageClient = None


@dataclass
class LineageConfig:
    """Configuration for OpenLineage client."""
    endpoint: str = os.getenv("OPENLINEAGE_ENDPOINT", "http://localhost:5000")
    api_key: Optional[str] = os.getenv("OPENLINEAGE_API_KEY")
    namespace: str = os.getenv("OPENLINEAGE_NAMESPACE", "data-platform")
    producer: str = "https://github.com/OpenLineage/OpenLineage/tree/main/integration/python"


class LineageTracker:
    """Track data lineage using OpenLineage."""

    def __init__(self, config: Optional[LineageConfig] = None):
        self.config = config or LineageConfig()
        self.client = None
        if OPENLINEAGE_AVAILABLE:
            try:
                self.client = OpenLineageClient(url=self.config.endpoint)
            except Exception as e:
                print(f"Warning: Could not initialize OpenLineage client: {e}")

    def emit_start(
        self,
        job_name: str,
        inputs: List[Dataset] = None,
        outputs: List[Dataset] = None,
        run_id: str = None,
        job_facets: Dict = None,
    ) -> str:
        """Emit a START run event."""
        run_id = run_id or str(uuid.uuid4())
        if not self.client:
            return run_id

        job = Job(namespace=self.config.namespace, name=job_name)
        run = Run(runId=run_id)

        event = RunEvent(
            eventType=RunState.START,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            producer=self.config.producer,
            inputs=inputs or [],
            outputs=outputs or [],
            jobFacets=job_facets or {},
        )

        try:
            self.client.emit(event)
        except Exception as e:
            print(f"Warning: Failed to emit START event: {e}")

        return run_id

    def emit_complete(
        self,
        job_name: str,
        run_id: str,
        inputs: List[Dataset] = None,
        outputs: List[Dataset] = None,
        run_facets: Dict = None,
    ):
        """Emit a COMPLETE run event."""
        if not self.client:
            return

        job = Job(namespace=self.config.namespace, name=job_name)
        run = Run(runId=run_id)

        event = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            producer=self.config.producer,
            inputs=inputs or [],
            outputs=outputs or [],
            runFacets=run_facets or {},
        )

        try:
            self.client.emit(event)
        except Exception as e:
            print(f"Warning: Failed to emit COMPLETE event: {e}")

    def emit_fail(
        self,
        job_name: str,
        run_id: str,
        error_message: str,
        inputs: List[Dataset] = None,
        outputs: List[Dataset] = None,
    ):
        """Emit a FAIL run event."""
        if not self.client:
            return

        job = Job(namespace=self.config.namespace, name=job_name)
        run = Run(runId=run_id)

        event = RunEvent(
            eventType=RunState.FAIL,
            eventTime=datetime.utcnow().isoformat() + "Z",
            run=run,
            job=job,
            producer=self.config.producer,
            inputs=inputs or [],
            outputs=outputs or [],
            runFacets={
                "errorMessage": ErrorMessageRunFacet(
                    message=error_message,
                    programmingLanguage="PYTHON",
                )
            },
        )

        try:
            self.client.emit(event)
        except Exception as e:
            print(f"Warning: Failed to emit FAIL event: {e}")

    def create_dataset(
        self,
        name: str,
        namespace: str = None,
        fields: List[Dict[str, str]] = None,
        source_facets: Dict = None,
    ) -> Dataset:
        """Create a Dataset with optional schema and source facets."""
        namespace = namespace or self.config.namespace
        facets = {}

        if fields:
            schema_fields = [SchemaField(name=f["name"], type=f["type"]) for f in fields]
            facets["schema"] = SchemaDatasetFacet(fields=schema_fields)

        if source_facets:
            facets.update(source_facets)
        else:
            facets["dataSource"] = DataSourceDatasetFacet(
                name="postgresql",
                uri="postgresql://datawarehouse",
            )

        return Dataset(namespace=namespace, name=name, facets=facets)

    def create_sql_job_facet(self, query: str) -> Dict:
        """Create a SQL job facet."""
        return {"sql": SQLJobFacet(query=query)}


def get_lineage_tracker() -> LineageTracker:
    """Get a singleton LineageTracker instance."""
    return LineageTracker()


# Convenience functions for common operations
def track_ingestion(
    source_name: str,
    target_table: str,
    run_id: str = None,
    row_count: int = None,
) -> str:
    """Track data ingestion from source to raw table."""
    tracker = get_lineage_tracker()

    inputs = [tracker.create_dataset(name=source_name, namespace="source")]
    outputs = [
        tracker.create_dataset(
            name=target_table,
            fields=[
                {"name": "transaction_id", "type": "VARCHAR"},
                {"name": "transaction_date", "type": "DATE"},
                {"name": "customer_id", "type": "VARCHAR"},
                {"name": "product_id", "type": "VARCHAR"},
                {"name": "quantity", "type": "INTEGER"},
                {"name": "unit_price", "type": "DECIMAL"},
            ],
        )
    ]

    job_facets = {}
    if row_count:
        job_facets["rowCount"] = {"rowCount": row_count}

    return tracker.emit_start("ingestion", inputs, outputs, run_id, job_facets)


def track_transformation(
    job_name: str,
    input_tables: List[str],
    output_table: str,
    sql_query: str = None,
    run_id: str = None,
) -> str:
    """Track data transformation."""
    tracker = get_lineage_tracker()

    inputs = [tracker.create_dataset(name=t) for t in input_tables]
    outputs = [tracker.create_dataset(name=output_table)]

    job_facets = {}
    if sql_query:
        job_facets.update(tracker.create_sql_job_facet(sql_query))

    return tracker.emit_start(job_name, inputs, outputs, run_id, job_facets)


def track_quality_check(
    table_name: str,
    checks: List[str],
    passed: bool,
    run_id: str = None,
):
    """Track data quality check results."""
    tracker = get_lineage_tracker()

    inputs = [tracker.create_dataset(name=table_name)]
    outputs = []

    if passed:
        tracker.emit_complete("quality_check", run_id, inputs, outputs)
    else:
        tracker.emit_fail(
            "quality_check",
            run_id,
            f"Quality checks failed: {', '.join(checks)}",
            inputs,
            outputs,
        )