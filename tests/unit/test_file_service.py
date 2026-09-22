import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch

from app.services.file_service import FileUploadService
from app.schemas.file_upload import FileUploadResponse


class TestFileUploadService:

    @patch("app.services.file_service.Minio")
    @patch("app.services.file_service.ensure_bucket")
    @patch("app.services.file_service.DataLakeClient" if False else "app.services.file_service.Minio")
    def test_compute_checksum(self, mock_minio):
        service = FileUploadService(Mock())
        content = b"test content"
        checksum = service._compute_checksum(content)
        assert len(checksum) == 64

    @patch("app.services.file_service.Minio")
    def test_inspect_csv_valid(self, mock_minio):
        service = FileUploadService(Mock())
        csv_content = b"transaction_id,quantity\nTX001,2\nTX002,1\n"
        row_count, columns = service._inspect_csv(csv_content)
        assert row_count == 2
        assert "transaction_id" in columns

    def test_inspect_csv_invalid(self):
        service = FileUploadService(Mock())
        row_count, columns = service._inspect_csv(b"invalid binary data \x00\x01")
        assert row_count is None
        assert columns is None


class TestRawStorageService:

    @patch("app.services.raw_storage_service.Minio")
    @patch("app.services.raw_storage_service.ensure_bucket")
    def test_bucket_property(self, mock_ensure, mock_minio_cls):
        service = RawStorageService(Mock())
        assert service.bucket == "bronze"

    def test_inspect_file_csv(self):
        service = RawStorageService(Mock())
        csv_content = b"col1,col2\na,1\nb,2\n"
        rows, cols = service._inspect_file(csv_content, "text/csv")
        assert rows == 2
        assert cols == ["col1", "col2"]

    def test_inspect_file_non_csv(self):
        service = RawStorageService(Mock())
        rows, cols = service._inspect_file(b"binary", "application/octet-stream")
        assert rows is None
        assert cols is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
