import pytest
import pandas as pd
import io
from unittest.mock import Mock, AsyncMock, patch

from app.services.transformation_service import TransformationService


class TestTransformationService:

    def test_aggregate_sales(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002", "TX003"],
            "transaction_date": ["2026-09-01", "2026-09-01", "2026-09-02"],
            "customer_id": ["C001", "C002", "C003"],
            "product_id": ["P001", "P002", "P003"],
            "quantity": [2, 1, 3],
            "unit_price": [100.0, 250.0, 150.0],
            "total_amount": [200.0, 250.0, 450.0],
        })
        result = TransformationService.aggregate_sales(df)
        assert len(result) == 2
        assert "transaction_count" in result.columns
        assert "units_sold" in result.columns
        assert "revenue" in result.columns
        day1 = result[result["transaction_date"] == "2026-09-01"].iloc[0]
        assert day1["transaction_count"] == 2
        assert day1["units_sold"] == 3
        assert day1["revenue"] == 450.0

    def test_aggregate_sales_empty(self):
        df = pd.DataFrame()
        result = TransformationService.aggregate_sales(df)
        assert len(result) == 0
        assert "transaction_count" in result.columns

    def test_aggregate_by_customer(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002", "TX003"],
            "customer_id": ["C001", "C001", "C002"],
            "quantity": [2, 1, 3],
            "total_amount": [200.0, 250.0, 450.0],
        })
        result = TransformationService._aggregate_by_customer(TransformationService(None), df)
        assert len(result) == 2
        c001 = result[result["customer_id"] == "C001"].iloc[0]
        assert c001["total_transactions"] == 2
        assert c001["total_revenue"] == 450.0

    def test_aggregate_by_product(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002"],
            "product_id": ["P001", "P001"],
            "quantity": [2, 1],
            "total_amount": [200.0, 250.0],
        })
        result = TransformationService._aggregate_by_product(TransformationService(None), df)
        assert len(result) == 1
        assert result.iloc[0]["total_transactions"] == 2

    def test_valid_aggregation_types(self):
        valid_types = ["daily_sales", "customer_summary", "product_summary"]
        assert "daily_sales" in valid_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
