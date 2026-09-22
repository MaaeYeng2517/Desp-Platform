# Copyright (c) 2026 Data Engineering Workflow Platform
# Licensed under the MIT License

"""
Unit tests for quality checks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

from quality.sales_quality import check_quality
from quality.gold_quality import run_quality


@contextmanager
def mock_connection_context(mock_conn):
    """Mock context manager for database connection."""
    yield mock_conn


class TestSalesQuality:
    @patch("quality.sales_quality.create_engine")
    def test_check_quality_all_pass(self, mock_create_engine):
        """Test quality checks pass when all validations succeed."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        # All checks return 0 (no violations)
        mock_conn.execute.return_value.scalar.return_value = 0

        check_quality()

        # Verify all 4 checks were executed
        assert mock_conn.execute.call_count == 4

    @patch("quality.sales_quality.create_engine")
    def test_check_quality_fails_duplicate(self, mock_create_engine):
        """Test quality check fails on duplicate transactions."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        # First check (duplicates) returns 1, rest return 0
        mock_conn.execute.return_value.scalar.side_effect = [1, 0, 0, 0]

        with pytest.raises(ValueError, match="Quality check failed: duplicate_transaction"):
            check_quality()

    @patch("quality.sales_quality.create_engine")
    def test_check_quality_fails_invalid_quantity(self, mock_create_engine):
        """Test quality check fails on invalid quantity."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        # Second check (quantity) returns 1
        mock_conn.execute.return_value.scalar.side_effect = [0, 1, 0, 0]

        with pytest.raises(ValueError, match="Quality check failed: invalid_quantity"):
            check_quality()

    @patch("quality.sales_quality.create_engine")
    def test_check_quality_fails_invalid_price(self, mock_create_engine):
        """Test quality check fails on negative price."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        # Third check (price) returns 1
        mock_conn.execute.return_value.scalar.side_effect = [0, 0, 1, 0]

        with pytest.raises(ValueError, match="Quality check failed: invalid_price"):
            check_quality()

    @patch("quality.sales_quality.create_engine")
    def test_check_quality_fails_null_customer(self, mock_create_engine):
        """Test quality check fails on null customer_id."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        # Fourth check (null customer) returns 1
        mock_conn.execute.return_value.scalar.side_effect = [0, 0, 0, 1]

        with pytest.raises(ValueError, match="Quality check failed: null_customer"):
            check_quality()


class TestGoldQuality:
    @patch("quality.gold_quality.create_engine")
    def test_run_quality_all_pass(self, mock_create_engine):
        """Test gold quality checks pass."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        mock_conn.execute.return_value.scalar.return_value = 0

        run_quality()

        assert mock_conn.execute.call_count == 3

    @patch("quality.gold_quality.create_engine")
    def test_run_quality_fails_negative_revenue(self, mock_create_engine):
        """Test gold quality fails on negative revenue."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        mock_conn.execute.return_value.scalar.side_effect = [1, 0, 0]

        with pytest.raises(Exception, match="QUALITY FAILED: no_negative_revenue"):
            run_quality()

    @patch("quality.gold_quality.create_engine")
    def test_run_quality_fails_negative_units(self, mock_create_engine):
        """Test gold quality fails on negative units."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        mock_conn.execute.return_value.scalar.side_effect = [0, 1, 0]

        with pytest.raises(Exception, match="QUALITY FAILED: no_negative_units"):
            run_quality()

    @patch("quality.gold_quality.create_engine")
    def test_run_quality_fails_null_date(self, mock_create_engine):
        """Test gold quality fails on null date."""
        mock_engine = Mock()
        mock_conn = Mock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value = mock_connection_context(mock_conn)

        mock_conn.execute.return_value.scalar.side_effect = [0, 0, 1]

        with pytest.raises(Exception, match="QUALITY FAILED: no_null_date"):
            run_quality()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])