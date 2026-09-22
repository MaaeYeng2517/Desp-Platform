# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Unit tests for ingestion pipeline.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from ingestion.sales_pipeline_minio import (
    extract,
    validate,
    transform,
    load_to_postgres,
    load_to_minio,
)


class TestExtract:
    def test_extract_returns_dataframe(self):
        """Test that extract returns a DataFrame with expected columns."""
        with patch("ingestion.sales_pipeline_minio.pd.read_csv") as mock_read:
            mock_read.return_value = pd.DataFrame({
                "transaction_id": ["TX001"],
                "transaction_date": ["2026-09-01"],
                "customer_id": ["C001"],
                "product_id": ["P001"],
                "quantity": [2],
                "unit_price": [100.00],
            })
            df = extract()
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
            assert list(df.columns) == [
                "transaction_id",
                "transaction_date",
                "customer_id",
                "product_id",
                "quantity",
                "unit_price",
            ]


class TestValidate:
    def test_validate_passes_valid_data(self):
        """Test validation passes for valid data."""
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002"],
            "transaction_date": ["2026-09-01", "2026-09-02"],
            "customer_id": ["C001", "C002"],
            "product_id": ["P001", "P002"],
            "quantity": [2, 1],
            "unit_price": [100.00, 250.00],
        })
        assert validate(df) is True

    def test_validate_fails_missing_columns(self):
        """Test validation fails for missing columns."""
        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "customer_id": ["C001"],
        })
        with pytest.raises(ValueError, match="Missing columns"):
            validate(df)

    def test_validate_fails_duplicate_transaction_id(self):
        """Test validation fails for duplicate transaction_id."""
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX001"],
            "transaction_date": ["2026-09-01", "2026-09-02"],
            "customer_id": ["C001", "C002"],
            "product_id": ["P001", "P002"],
            "quantity": [2, 1],
            "unit_price": [100.00, 250.00],
        })
        with pytest.raises(ValueError, match="Duplicate transaction_id"):
            validate(df)

    def test_validate_fails_invalid_quantity(self):
        """Test validation fails for quantity <= 0."""
        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": ["2026-09-01"],
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [0],
            "unit_price": [100.00],
        })
        with pytest.raises(ValueError, match="Quantity must be greater than zero"):
            validate(df)

    def test_validate_fails_negative_price(self):
        """Test validation fails for negative unit_price."""
        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": ["2026-09-01"],
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [2],
            "unit_price": [-100.00],
        })
        with pytest.raises(ValueError, match="Unit price cannot be negative"):
            validate(df)


class TestTransform:
    def test_transform_adds_total_amount(self):
        """Test transform adds total_amount column."""
        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": ["2026-09-01"],
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [2],
            "unit_price": [100.00],
        })
        result = transform(df)
        assert "total_amount" in result.columns
        assert result["total_amount"].iloc[0] == 200.00

    def test_transform_converts_date(self):
        """Test transform converts transaction_date to datetime."""
        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": ["2026-09-01"],
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [2],
            "unit_price": [100.00],
        })
        result = transform(df)
        assert pd.api.types.is_datetime64_any_dtype(result["transaction_date"])


class TestLoadToPostgres:
    @patch("ingestion.sales_pipeline_minio.create_engine")
    @patch("pandas.DataFrame.to_sql")
    def test_load_to_postgres_calls_to_sql(self, mock_to_sql, mock_create_engine):
        """Test load_to_postgres calls to_sql with correct parameters."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": pd.to_datetime(["2026-09-01"]),
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [2],
            "unit_price": [100.00],
            "total_amount": [200.00],
        })

        load_to_postgres(df)

        mock_create_engine.assert_called_once()
        mock_to_sql.assert_called_once()


class TestLoadToMinio:
    @patch("ingestion.sales_pipeline_minio.get_minio_client")
    @patch("ingestion.sales_pipeline_minio.Path.mkdir")
    @patch("pandas.DataFrame.to_csv")
    def test_load_to_minio_uploads_file(self, mock_to_csv, mock_mkdir, mock_get_client):
        """Test load_to_minio uploads file to MinIO."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        df = pd.DataFrame({
            "transaction_id": ["TX001"],
            "transaction_date": pd.to_datetime(["2026-09-01"]),
            "customer_id": ["C001"],
            "product_id": ["P001"],
            "quantity": [2],
            "unit_price": [100.00],
            "total_amount": [200.00],
        })

        load_to_minio(df, mock_client)

        mock_mkdir.assert_called_once()
        mock_to_csv.assert_called_once()
        mock_client.fput_object.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])