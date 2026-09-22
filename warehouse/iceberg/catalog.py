"""
Iceberg catalog configuration and loader.

Supports three catalog backends selectable via environment variables:

    ICEBERG_CATALOG_TYPE   - rest | sql | memory  (default: rest)
    ICEBERG_CATALOG_URI    - REST endpoint URL (required for REST)
    ICEBERG_WAREHOUSE      - Warehouse root path (S3 or local)
    ICEBERG_S3_ENDPOINT    - MinIO/S3 endpoint
    ICEBERG_S3_ACCESS_KEY  - S3 access key
    ICEBERG_S3_SECRET_KEY  - S3 secret key
    ICEBERG_S3_REGION      - S3 region (default: us-east-1)
    ICEBERG_S3_USE_SSL     - Use HTTPS (default: false)

The warehouse location defaults to ``s3://warehouse/`` so that Iceberg
metadata and data files live in MinIO alongside the existing bronze,
silver, and gold buckets.
"""

from __future__ import annotations

import os
from typing import Any

from pyiceberg.catalog import Catalog, load_catalog
from pyiceberg.io import FileIO
from pyiceberg.table import Namespace

__all__ = [
    "IcebergConfig",
    "get_catalog",
    "IcebergCatalogManager",
]


# Property keys understood by pyiceberg's S3 file IO
_S3_ENDPOINT = "s3.endpoint"
_S3_ACCESS_KEY_ID = "s3.access-key-id"
_S3_SECRET_ACCESS_KEY = "s3.secret-access-key"
_S3_REGION = "s3.region"
_S3_USE_SSL = "s3.use-ssl"
_S3_ALLOW_HTTP = "s3.allow-http"
_S3_SIGNER_ENDPOINT = "s3.signer-endpoint"


class IcebergConfig:
    """Configuration for Iceberg catalog and S3/MinIO storage."""

    def __init__(self, **overrides: Any) -> None:
        self.catalog_type: str = overrides.get(
            "catalog_type", os.getenv("ICEBERG_CATALOG_TYPE", "rest")
        )
        self.rest_uri: str = overrides.get(
            "rest_uri", os.getenv("ICEBERG_CATALOG_URI", "http://nessie:19120")
        )
        self.warehouse_location: str = overrides.get(
            "warehouse_location",
            os.getenv("ICEBERG_WAREHOUSE", "s3://warehouse/"),
        )
        self.s3_endpoint: str = overrides.get(
            "s3_endpoint", os.getenv("ICEBERG_S3_ENDPOINT", "localhost:9000")
        )
        self.s3_access_key: str = overrides.get(
            "s3_access_key", os.getenv("ICEBERG_S3_ACCESS_KEY", "minioadmin")
        )
        self.s3_secret_key: str = overrides.get(
            "s3_secret_key", os.getenv("ICEBERG_S3_SECRET_KEY", "minioadmin")
        )
        self.s3_region: str = overrides.get(
            "s3_region", os.getenv("ICEBERG_S3_REGION", "us-east-1")
        )
        self.s3_use_ssl: bool = overrides.get(
            "s3_use_ssl",
            os.getenv("ICEBERG_S3_USE_SSL", "false").lower() == "true",
        )
        self.namespace: str = overrides.get(
            "namespace", os.getenv("ICEBERG_NAMESPACE", "data_platform")
        )

    @property
    def is_s3(self) -> bool:
        return self.warehouse_location.startswith("s3://")

    def s3_properties(self) -> dict[str, str]:
        """Return S3 connection properties for pyiceberg file IO."""
        props: dict[str, str] = {
            _S3_ENDPOINT: self.s3_endpoint,
            _S3_ACCESS_KEY_ID: self.s3_access_key,
            _S3_SECRET_ACCESS_KEY: self.s3_secret_key,
            _S3_REGION: self.s3_region,
            _S3_USE_SSL: str(self.s3_use_ssl).lower(),
            _S3_ALLOW_HTTP: "true" if not self.s3_use_ssl else "false",
        }
        return props


def _build_common_properties(config: IcebergConfig) -> dict[str, Any]:
    props: dict[str, Any] = {
        "warehouse": config.warehouse_location,
    }
    props.update(config.s3_properties())
    return props


def get_catalog(name: str = "iceberg") -> Catalog:
    """
    Return a configured pyiceberg ``Catalog``.

    The backend is selected by ``ICEBERG_CATALOG_TYPE``:

    * ``rest``   - connects to an Apache Iceberg REST catalog
      (e.g. Project Nessie). Falls back to in-memory if the server
      is unreachable *and* ``ICEBERG_CATALOG_FALLBACK`` is set.
    * ``sql``    - uses a SQLAlchemy-compatible database as the
      metastore (PostgreSQL / SQLite).
    * ``memory`` - in-process catalog; useful for tests.
    """
    config = IcebergConfig()
    catalog_type = config.catalog_type

    if catalog_type == "rest":
        properties: dict[str, Any] = {
            "type": "rest",
            "uri": config.rest_uri,
        }
        properties.update(_build_common_properties(config))

        try:
            return load_catalog(name, **properties)
        except Exception:
            if os.getenv("ICEBERG_CATALOG_FALLBACK", "false").lower() == "true":
                return _load_memory_catalog(name)
            raise

    if catalog_type == "sql":
        properties = {
            "type": "sql",
            "uri": os.getenv(
                "ICEBERG_SQL_URI",
                "postgresql+psycopg2://dataeng:dataeng@localhost:5432/iceberg_catalog",
            ),
        }
        properties.update(_build_common_properties(config))
        return load_catalog(name, **properties)

    return _load_memory_catalog(name)


def _load_memory_catalog(name: str) -> Catalog:
    local_warehouse = os.getenv(
        "ICEBERG_LOCAL_WAREHOUSE", "/tmp/iceberg_catalog"
    )
    return load_catalog(
        name,
        type="in-memory",
        warehouse=f"file://{local_warehouse}",
    )


class IcebergCatalogManager:
    """
    High-level helper for interacting with the Iceberg catalog.

    Provides convenience methods for table lifecycle operations
    (create, load, drop, list) that are used throughout the pipeline.
    """

    def __init__(self, catalog: Catalog | None = None) -> None:
        self.catalog = catalog or get_catalog()

    def create_table(
        self,
        identifier: str,
        schema: Any = None,
        partition_spec: Any = None,
        location: str | None = None,
    ) -> Any:
        """Create a new Iceberg table."""
        config = IcebergConfig()
        properties: dict[str, Any] = {
            "format-version": "2",
            "write.target-file-size-bytes": "134217728",
            "commit.retry.num-retries": "3",
        }
        if location:
            properties["location"] = location
        properties.update(config.s3_properties())
        return self.catalog.create_table(
            identifier=identifier,
            schema=schema,
            partition_spec=partition_spec,
            properties=properties,
        )

    def table_exists(self, identifier: str) -> bool:
        try:
            self.catalog.load_table(identifier)
            return True
        except Exception:
            return False

    def list_tables(self, namespace: str | None = None) -> list[str]:
        ns = namespace or IcebergConfig().namespace
        return [
            f"{tbl.namespace}.{tbl.name}"
            for tbl in self.catalog.list_tables(Namespace(ns))
        ]

    def drop_table(self, identifier: str) -> None:
        self.catalog.drop_table(identifier)
