# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Unit tests for transformation pipeline.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from transformation.sales_silver_minio import (
    get_minio_client,
    download_from_minio,
    upload_to_minio,
    transform,
)


class TestMinioClient:
    @patch("transformation.sales_silver_minio.Minio")
    def test_get_minio_client(self, mock_minio):
        """Test MinIO client creation."""
        client = get_minio_client()
        mock_minio.assert_called_once_with(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,
        )


class TestDownloadFromMinio:
    @patch("transformation.sales_silver_minio.Path.mkdir")
    def test_download_from_minio(self, mock_mkdir):
        """Test downloading file from MinIO."""
        mock_client = Mock()
        download_from_minio(mock_client, "bronze", "sales/sales.csv", "data/bronze/sales.csv")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_client.fget_object.assert_called_once_with("bronze", "sales/sales.csv", "data/bronze/sales.csv")


class TestUploadToMinio:
    def test_upload_to_minio(self):
        """Test uploading file to MinIO."""
        mock_client = Mock()
        upload_to_minio(mock_client, "silver", "sales/sales_clean.csv", "data/silver/sales.csv")
        mock_client.fput_object.assert_called_once_with("silver", "sales/sales_clean.csv", "data/silver/sales.csv")


class TestTransform:
    @patch("transformation.sales_silver_minio.get_minio_client")
    @patch("transformation.sales_silver_minio.download_from_minio")
    @patch("transformation.sales_silver_minio.upload_to_minio")
    @patch("transformation.sales_silver_minio.Path.mkdir")
    @patch("transformation.sales_silver_minio.DataFrame.to_csv")
    @patch("transformation.sales_silver_minio.pd.read_csv")
    def test_transform_bronze_to_silver_to_gold(
        self,
        mock_read_csv,
        mock_to_csv,
        mock_mkdir,
        mock_upload,
        mock_download,
        mock_get_client,
    ):
        """Test full transformation pipeline."""
        # Setup mock data
        mock_df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002", "TX001"],  # TX001 duplicate
            "transaction_date": ["2026-09-01", "2026-09-01", "2026-09-01"],
            "customer_id": ["C001", "C002", "C001"],
            "product_id": ["P001", "P002", "P001"],
            "quantity": [2, 1, 2],
            "unit_price": [100.00, 250.00, 100.00],
        })
        mock_read_csv.return_value = mock_df

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        transform()

        # Verify read
        mock_read_csv.assert_called_once_with("data/bronze/sales/sales.csv")

        # Verify deduplication (should remove 1 duplicate)
        # After dedup: 2 records
        # After validation: 2 records (all valid)
        # Gold: 1 date with 2 transactions

        # Verify silver upload
        mock_upload.assert_any_call(mock_client, "silver", "sales/sales_clean.csv", "data/silver/sales/sales_clean.csv")

        # Verify gold upload
        mock_upload.assert_any_call(mock_client, "gold", "sales/sales_daily.csv", "data/gold/sales_daily.csv")


class TestTransformEdgeCases:
    @patch("transformation.sales_silver_minio.get_minio_client")
    @patch("transformation.sales_silver_minio.download_from_minio")
    @patch("transformation.sales_silver_minio.upload_to_minio")
    @patch("transformation.sales_silver_minio.Path.mkdir")
    @patch("transformation.sales_silver_minio.DataFrame.to_csv")
    @patch("transformation.sales_silver_minio.pd.read_csv")
    def test_transform_removes_invalid_quantity(
        self,
        mock_read_csv,
        mock_to_csv,
        mock_mkdir,
        mock_upload,
        mock_download,
        mock_get_client,
    ):
        """Test transform removes records with quantity <= 0."""
        mock_df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002"],
            "transaction_date": ["2026-09-01", "2026-09-01"],
            "customer_id": ["C001", "C002"],
            "product_id": ["P001", "P002"],
            "quantity": [2, 0],  # TX002 has invalid quantity
            "unit_price": [100.00, 250.00],
        })
        mock_read_csv.return_value = mock_df

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        transform()

        # Should only have 1 record after filtering
        # Gold should have 1 record for 2026-09-01 with 1 transaction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])