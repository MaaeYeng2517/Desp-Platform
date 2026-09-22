"""
Apache Iceberg integration for the Data Engineering Workflow Platform.

This package provides Python-level Iceberg table management on top of
MinIO (S3-compatible object storage). It supports the full Medallion
Architecture (bronze -> silver -> gold) using Iceberg table format
with snapshot isolation, schema evolution, and time-travel.

Catalog backends:
    - REST  : Apache Iceberg REST catalog (e.g. Nessie, Iceberg REST server)
    - SQL   : SQLAlchemy-backed catalog (PostgreSQL / SQLite)
    - Memory: In-process in-memory catalog (testing only)

Usage:
    from warehouse.iceberg.catalog import get_catalog

    catalog = get_catalog()
    table = catalog.load_table("bronze.sales")
    df = table.scan().to_df()
"""

from warehouse.iceberg.catalog import get_catalog, IcebergCatalogManager
from warehouse.iceberg.schema import SALES_SCHEMA, SalesSchema
from warehouse.iceberg.manager import IcebergTableManager

__all__ = [
    "get_catalog",
    "IcebergCatalogManager",
    "SALES_SCHEMA",
    "SalesSchema",
    "IcebergTableManager",
]
