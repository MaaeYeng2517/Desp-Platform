import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.metadata_service import MetadataService
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditAction, AuditStatus


class TestMetadataService:

    def test_extract_from_file_returns_schema(self):
        from unittest.mock import MagicMock

        mock_file = MagicMock()
        mock_file.dataset_id = uuid4()

        service = MetadataService(Mock())

        import pandas as pd
        import io

        mock_client = Mock()
        mock_response = Mock()
        csv_data = b"transaction_id,quantity\nTX001,2\nTX002,1\n"
        mock_response.read.return_value = csv_data
        mock_client.get_object.return_value = mock_response

        with patch("app.services.metadata_service.Minio", return_value=mock_client):
            schema, count = service._extract_from_file(mock_file)

        assert count == 2
        assert len(schema) == 2
        assert schema[0]["name"] == "transaction_id"
        assert schema[0]["type"] == "string"
        assert schema[1]["name"] == "quantity"
        assert schema[1]["type"] == "integer"


class TestAuditService:

    @pytest.mark.asyncio
    async def test_log_creates_record(self):
        mock_db = AsyncMock()
        service = AuditService(mock_db)

        await service.log(
            action="create",
            resource_type="dataset",
            status="success",
            user="test_user",
            dataset_id=uuid4(),
        )

        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=AsyncMock(return_value=None)))
        service = AuditService(mock_db)

        result = await service.get_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_query_with_filters(self):
        from app.schemas.audit_log import AuditLogFilter
        from app.models.audit_log import AuditLog

        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        service = AuditService(mock_db)
        filter = AuditLogFilter(action="create", user="test_user")
        results = await service.query(filter=filter, limit=10, offset=0)
        assert results == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
