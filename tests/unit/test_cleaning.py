import pytest
import pandas as pd
import io
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.cleaning_service import CleaningService
from app.schemas.validation import CleaningRequest


class TestCleaningService:

    def test_clean_dataframe_deduplication(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX001", "TX002"],
            "quantity": [2, 2, 1],
        })
        request = CleaningRequest(remove_duplicates=True)
        cleaned = CleaningService.clean_dataframe(df, request)
        assert len(cleaned) == 2

    def test_clean_dataframe_drop_nulls(self):
        df = pd.DataFrame({
            "id": [1, None, 3],
            "name": ["a", "b", None],
        })
        request = CleaningRequest(drop_nulls=["id"])
        cleaned = CleaningService.clean_dataframe(df, request)
        assert len(cleaned) == 2
        assert cleaned["id"].iloc[0] == 1

    def test_clean_dataframe_fill_nulls(self):
        df = pd.DataFrame({"id": [1, None, 3], "name": ["a", None, "c"]})
        request = CleaningRequest(fill_nulls={"name": "unknown"})
        cleaned = CleaningService.clean_dataframe(df, request)
        assert cleaned["name"].iloc[1] == "unknown"

    def test_clean_dataframe_normalize_dates(self):
        df = pd.DataFrame({"date_col": ["2026-01-01", "2026-01-02"]})
        request = CleaningRequest(normalize_dates=True)
        cleaned = CleaningService.clean_dataframe(df, request)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["date_col"])

    def test_clean_dataframe_drop_columns(self):
        df = pd.DataFrame({"keep": [1, 2], "drop": [3, 4]})
        request = CleaningRequest(columns_to_drop=["drop"])
        cleaned = CleaningService.clean_dataframe(df, request)
        assert "drop" not in cleaned.columns
        assert "keep" in cleaned.columns

    def test_clean_dataframe_no_operations(self):
        df = pd.DataFrame({"id": [1, 2]})
        request = CleaningRequest()
        cleaned = CleaningService.clean_dataframe(df, request)
        assert len(cleaned) == 2

    def test_get_default_cleaning_request_sales(self):
        request = CleaningService.get_default_cleaning_request("sales")
        assert request.remove_duplicates is True
        assert request.normalize_dates is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
