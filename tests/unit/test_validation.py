import pytest
import pandas as pd
import io
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from app.services.validation_service import ValidationService
from app.schemas.validation import ValidationResult, ValidationStatus


class TestValidationService:

    def test_validate_valid_dataframe(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", "TX002"],
            "transaction_date": ["2026-09-01", "2026-09-02"],
            "customer_id": ["C001", "C002"],
            "product_id": ["P001", "P002"],
            "quantity": [2, 1],
            "unit_price": [100.00, 250.00],
        })
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["transaction_id", "customer_id", "quantity", "unit_price"],
        )
        assert result.status == ValidationStatus.PASSED
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_validate_missing_columns(self):
        df = pd.DataFrame({"transaction_id": ["TX001"]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["transaction_id", "customer_id"],
        )
        assert result.status == ValidationStatus.FAILED
        assert len(result.errors) == 1
        assert "missing_columns" in result.errors[0]["type"]

    def test_validate_null_values(self):
        df = pd.DataFrame({
            "transaction_id": ["TX001", None],
            "customer_id": ["C001", None],
        })
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["transaction_id", "customer_id"],
        )
        assert result.status == ValidationStatus.FAILED
        assert result.failed_records > 0

    def test_validate_unique_violations(self):
        df = pd.DataFrame({"id": [1, 1, 2]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["id"],
            column_validations=[{"column_name": "id", "unique": True}],
        )
        assert result.status == ValidationStatus.FAILED

    def test_validate_range_check(self):
        df = pd.DataFrame({"qty": [1, -5, 3]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["qty"],
            column_validations=[{"column_name": "qty", "min_value": 0}],
        )
        assert result.status == ValidationStatus.FAILED

    def test_validate_regex_pattern(self):
        df = pd.DataFrame({"tx_id": ["TX001", "INVALID", "TX003"]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["tx_id"],
            column_validations=[{"column_name": "tx_id", "regex_pattern": r"^TX\d+$"}],
        )
        assert result.status == ValidationStatus.WARNING
        assert len(result.warnings) == 1

    def test_validate_csv_content(self):
        csv_content = b"transaction_id,quantity\nTX001,2\nTX002,1\n"
        result = ValidationService.validate_csv_content(
            csv_content,
            required_columns=["transaction_id", "quantity"],
        )
        assert result.status == ValidationStatus.PASSED
        assert result.total_records == 2

    def test_validate_csv_parse_error(self):
        result = ValidationService.validate_csv_content(
            b"invalid,,csv,,content",
            required_columns=["nonexistent"],
        )
        assert result.status == ValidationStatus.FAILED

    def test_get_default_column_validations_sales(self):
        validations = ValidationService.get_default_column_validations("sales")
        assert len(validations) == 3
        assert validations[0]["column_name"] == "transaction_id"
        assert validations[1]["column_name"] == "quantity"

    def test_get_default_column_validations_unknown(self):
        validations = ValidationService.get_default_column_validations("unknown")
        assert validations == []

    def test_validate_positive_rule(self):
        df = pd.DataFrame({"amount": [100, -50, 0, 200]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["amount"],
            custom_rules=[{"type": "positive", "column": "amount"}],
        )
        assert result.status == ValidationStatus.FAILED
        assert result.failed_records == 2

    def test_validate_custom_expression(self):
        df = pd.DataFrame({"qty": [1, 2, 0], "price": [10, 0, 5]})
        result = ValidationService.validate_dataframe(
            df,
            required_columns=["qty", "price"],
            custom_rules=[{"type": "custom", "column": "qty", "expression": "qty > 0"}],
        )
        assert result.status == ValidationStatus.FAILED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
