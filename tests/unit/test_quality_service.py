import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from app.services.quality_service import QualityService
from app.schemas.quality import QualityStatus


class TestQualityService:

    def test_get_default_quality_rules_sales(self):
        rules = QualityService.get_default_quality_rules("sales")
        assert len(rules) == 4
        names = [r["name"] for r in rules]
        assert "unique_transaction_id" in names
        assert "positive_quantity" in names
        assert "non_negative_price" in names
        assert "not_null_customer" in names

    def test_get_default_quality_rules_unknown(self):
        rules = QualityService.get_default_quality_rules("unknown")
        assert rules == []

    def test_rule_config_structure(self):
        rules = QualityService.get_default_quality_rules("sales")
        positive_rule = [r for r in rules if r["rule_type"] == "positive"][0]
        assert positive_rule["column_name"] == "quantity"
        assert "rule_config" in positive_rule

        range_rule = [r for r in rules if r["rule_type"] == "range"][0]
        assert range_rule["column_name"] == "unit_price"
        assert range_rule["rule_config"]["min_value"] == 0

    def test_rule_types(self):
        rules = QualityService.get_default_quality_rules("sales")
        types = {r["rule_type"] for r in rules}
        assert "unique" in types
        assert "not_null" in types
        assert "range" in types
        assert "positive" in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
