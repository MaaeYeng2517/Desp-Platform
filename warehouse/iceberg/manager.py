"""
High-level Iceberg table manager for the Medallion Architecture.

Provides a unified API for creating, loading, appending, overwriting,
and scanning Iceberg tables across the bronze, silver, and gold layers.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from pyarrow import Table as ArrowTable
from pyiceberg.catalog import Catalog
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.table import SortOrder, Table
from pyiceberg.transforms import Transform

from warehouse.iceberg.catalog import IcebergCatalogManager, IcebergConfig, get_catalog
from warehouse.iceberg.schema import get_schema_for_layer

__all__ = [
    "IcebergTableManager",
    "IcebergTableOps",
]


_LAYER_NAMESPACE: dict[str, str] = {
    "bronze": "bronze",
    "silver": "silver",
    "gold": "gold",
}

_DEFAULT_PARTITION_FIELD_ID = 1000


def _default_partition_spec(
    schema: Any, partition_column: str | None = None
) -> PartitionSpec | None:
    """Return a partition spec, or ``None`` for unpartitioned tables."""
    if partition_column is None:
        return None
    for field in schema.columns:
        if field.name == partition_column:
            return PartitionSpec(
                PartitionField(
                    source_id=field.field_id,
                    field_id=_DEFAULT_PARTITION_FIELD_ID,
                    name=partition_column,
                    transform="day",
                )
            )
    return None


class IcebergTableManager(IcebergCatalogManager):
    """Extended catalog manager with table-level CRUD helpers."""

    def __init__(self, catalog: Catalog | None = None) -> None:
        super().__init__(catalog)
        self.config = IcebergConfig()

    # ------------------------------------------------------------------
    # Table identification
    # ------------------------------------------------------------------

    def _table_identifier(self, layer: str, name: str) -> str:
        namespace = _LAYER_NAMESPACE.get(layer, layer)
        return f"{namespace}.{name}"

    # ------------------------------------------------------------------
    # Table lifecycle
    # ------------------------------------------------------------------

    def create_table_for_layer(
        self,
        layer: str,
        name: str,
        location: str | None = None,
        partition_by: str | None = None,
    ) -> Table:
        """
        Create a new Iceberg table for the given Medallion layer.

        Parameters
        ----------
        layer : str
            One of ``bronze``, ``silver``, ``gold``.
        name : str
            Table name within the layer namespace.
        location : str, optional
            Override the warehouse location for this table.
        partition_by : str, optional
            Column name to partition by (using ``day`` transform).
        """
        schema = get_schema_for_layer(layer)
        identifier = self._table_identifier(layer, name)
        spec = _default_partition_spec(schema, partition_by)

        if location is None:
            location = f"{self.config.warehouse_location}{layer}/{name}"

        return self.create_table(
            identifier=identifier,
            schema=schema,
            partition_spec=spec,
            location=location,
        )

    def ensure_table(
        self,
        layer: str,
        name: str,
        location: str | None = None,
        partition_by: str | None = None,
    ) -> Table:
        """Create the table if it does not exist; otherwise load it."""
        identifier = self._table_identifier(layer, name)
        if self.table_exists(identifier):
            return self.catalog.load_table(identifier)
        return self.create_table_for_layer(
            layer, name, location=location, partition_by=partition_by
        )

    # ------------------------------------------------------------------
    # Data operations
    # ------------------------------------------------------------------

    def append_pandas(
        self,
        layer: str,
        name: str,
        df: pd.DataFrame,
        create_if_missing: bool = True,
        partition_by: str | None = None,
    ) -> None:
        """Append rows from a pandas DataFrame to an Iceberg table."""
        table = (
            self.ensure_table(layer, name, partition_by=partition_by)
            if create_if_missing
            else self.catalog.load_table(self._table_identifier(layer, name))
        )
        arrow_table = ArrowTable.from_pandas(df, preserve_index=False)
        table.append(arrow_table)

    def overwrite_pandas(
        self,
        layer: str,
        name: str,
        df: pd.DataFrame,
        create_if_missing: bool = True,
        partition_by: str | None = None,
    ) -> None:
        """Overwrite an entire Iceberg table with the contents of a DataFrame."""
        table = (
            self.ensure_table(layer, name, partition_by=partition_by)
            if create_if_missing
            else self.catalog.load_table(self._table_identifier(layer, name))
        )
        arrow_table = ArrowTable.from_pandas(df, preserve_index=False)
        table.overwrite(arrow_table)

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def scan_to_pandas(
        self,
        layer: str,
        name: str,
        selected_columns: list[str] | None = None,
        filters: Any = None,
    ) -> pd.DataFrame:
        """Scan an Iceberg table and return the result as a pandas DataFrame."""
        table = self.catalog.load_table(self._table_identifier(layer, name))
        task = table.scan(
            selected_columns=selected_columns,
            predicates=filters,
        )
        arrow_table = task.to_arrow_table()
        return arrow_table.to_pandas()

    def scan_to_arrow(
        self,
        layer: str,
        name: str,
        selected_columns: list[str] | None = None,
    ) -> ArrowTable:
        """Scan an Iceberg table and return the result as a pyarrow Table."""
        table = self.catalog.load_table(self._table_identifier(layer, name))
        task = table.scan(selected_columns=selected_columns)
        return task.to_arrow_table()

    # ------------------------------------------------------------------
    # Metadata / history
    # ------------------------------------------------------------------

    def get_snapshots(self, layer: str, name: str) -> list[Any]:
        """Return the list of snapshots for a table (time-travel support)."""
        table = self.catalog.load_table(self._table_identifier(layer, name))
        return list(table.metadata.snapshots)

    def time_travel(
        self,
        layer: str,
        name: str,
        snapshot_id: int,
    ) -> pd.DataFrame:
        """Read table data as it existed at a specific snapshot ID."""
        table = self.catalog.load_table(self._table_identifier(layer, name))
        task = table.scan(snapshot_id=snapshot_id)
        return task.to_arrow_table().to_pandas()


class IcebergTableOps:
    """
    Convenience facade that wraps an ``IcebergTableManager`` with the
    standard Bronze -> Silver -> Gold pipeline operations.
    """

    def __init__(self, manager: IcebergTableManager | None = None) -> None:
        self.manager = manager or IcebergTableManager()

    def bronze_write(self, df: pd.DataFrame, table_name: str = "sales") -> None:
        """Write raw data to the Bronze layer."""
        df = df.copy()
        if "loaded_at" not in df.columns:
            df["loaded_at"] = pd.Timestamp.now()
        self.manager.overwrite_pandas("bronze", table_name, df, partition_by="transaction_date")

    def silver_write(self, df: pd.DataFrame, table_name: str = "sales_clean") -> None:
        """Write cleaned data to the Silver layer."""
        df = df.copy()
        if "loaded_at" not in df.columns:
            df["loaded_at"] = pd.Timestamp.now()
        self.manager.overwrite_pandas("silver", table_name, df, partition_by="transaction_date")

    def gold_write(self, df: pd.DataFrame, table_name: str = "sales_daily") -> None:
        """Write aggregated data to the Gold layer."""
        df = df.copy()
        if "created_at" not in df.columns:
            df["created_at"] = pd.Timestamp.now()
        self.manager.overwrite_pandas("gold", table_name, df, partition_by="transaction_date")

    def bronze_read(self, table_name: str = "sales") -> pd.DataFrame:
        return self.manager.scan_to_pandas("bronze", table_name)

    def silver_read(self, table_name: str = "sales_clean") -> pd.DataFrame:
        return self.manager.scan_to_pandas("silver", table_name)

    def gold_read(self, table_name: str = "sales_daily") -> pd.DataFrame:
        return self.manager.scan_to_pandas("gold", table_name)
