"""
Iceberg table schema definitions for the Medallion Architecture layers.

Each layer (bronze, silver, gold) has its own schema derived from the
sales domain.  The schemas use Iceberg ``NestedField`` with explicit
field IDs so that schema evolution is fully supported.
"""

from __future__ import annotations

from pyiceberg.table import Schema
from pyiceberg.types import (
    DateType,
    DecimalType,
    IntegerType,
    NestedField,
    StringType,
    TimestampType,
)

__all__ = [
    "SALES_SCHEMA",
    "SALES_SILVER_SCHEMA",
    "SALES_GOLD_SCHEMA",
    "get_schema_for_layer",
    "SalesSchema",
]


# Bronze schema - raw, untransformed record as ingested from source.
# ``loaded_at`` tracks when the record first entered the Bronze layer.
SALES_SCHEMA: Schema = Schema(
    NestedField(field_id=1, name="transaction_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=2, name="transaction_date", field_type=DateType(), is_optional=False),
    NestedField(field_id=3, name="customer_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=4, name="product_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=5, name="quantity", field_type=IntegerType(), is_optional=False),
    NestedField(field_id=6, name="unit_price", field_type=DecimalType(12, 2), is_optional=False),
    NestedField(field_id=7, name="loaded_at", field_type=TimestampType(), is_optional=False),
)

# Silver schema - cleaned data with calculated ``total_amount``.
SALES_SILVER_SCHEMA: Schema = Schema(
    NestedField(field_id=1, name="transaction_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=2, name="transaction_date", field_type=DateType(), is_optional=False),
    NestedField(field_id=3, name="customer_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=4, name="product_id", field_type=StringType(), is_optional=False),
    NestedField(field_id=5, name="quantity", field_type=IntegerType(), is_optional=False),
    NestedField(field_id=6, name="unit_price", field_type=DecimalType(12, 2), is_optional=False),
    NestedField(field_id=7, name="total_amount", field_type=DecimalType(14, 2), is_optional=False),
    NestedField(field_id=8, name="loaded_at", field_type=TimestampType(), is_optional=False),
)

# Gold schema - daily aggregation.
SALES_GOLD_SCHEMA: Schema = Schema(
    NestedField(field_id=1, name="transaction_date", field_type=DateType(), is_optional=False),
    NestedField(field_id=2, name="transaction_count", field_type=IntegerType(), is_optional=False),
    NestedField(field_id=3, name="units_sold", field_type=IntegerType(), is_optional=False),
    NestedField(field_id=4, name="revenue", field_type=DecimalType(16, 2), is_optional=False),
    NestedField(field_id=5, name="created_at", field_type=TimestampType(), is_optional=False),
)

_LAYER_SCHEMAS: dict[str, Schema] = {
    "bronze": SALES_SCHEMA,
    "silver": SALES_SILVER_SCHEMA,
    "gold": SALES_GOLD_SCHEMA,
}


class SalesSchema:
    """Namespace for sales Iceberg schemas."""

    bronze: Schema = SALES_SCHEMA
    silver: Schema = SALES_SILVER_SCHEMA
    gold: Schema = SALES_GOLD_SCHEMA


def get_schema_for_layer(layer: str) -> Schema:
    """Return the Iceberg ``Schema`` for a given Medallion layer name."""
    layer_lower = layer.lower()
    if layer_lower not in _LAYER_SCHEMAS:
        raise ValueError(
            f"Unknown layer '{layer}'. Expected: bronze | silver | gold"
        )
    return _LAYER_SCHEMAS[layer_lower]
