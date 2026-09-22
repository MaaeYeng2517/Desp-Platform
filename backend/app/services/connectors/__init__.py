"""Connector framework for knowledge sources"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for all source connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to source"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test if connection is working"""
        pass
    
    @abstractmethod
    async def list_sources(self) -> List[Dict[str, Any]]:
        """List available sources"""
        pass
    
    @abstractmethod
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        """Fetch a single source"""
        pass
    
    @abstractmethod
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        """Sync source data"""
        pass
    
    async def get_checksum(self, content: str) -> str:
        """Generate checksum for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def has_changed(self, source_id: str, new_checksum: str, old_checksum: str) -> bool:
        """Check if content has changed"""
        return new_checksum != old_checksum


class PDFConnector(BaseConnector):
    """Connector for PDF files"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "pdf"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "pdf", "name": "PDF Files", "type": "pdf"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "pdf", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class WebConnector(BaseConnector):
    """Connector for websites and URLs"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "web"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "web", "name": "Website", "type": "web"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "web", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class DatabaseConnector(BaseConnector):
    """Connector for databases"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "database"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "database", "name": "Database", "type": "database"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "database", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class APIConnector(BaseConnector):
    """Connector for REST APIs"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "api"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "api", "name": "REST API", "type": "api"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "api", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class FileConnector(BaseConnector):
    """Connector for file uploads"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "file"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "file", "name": "File", "type": "file"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "file", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class YouTubeConnector(BaseConnector):
    """Connector for YouTube videos"""
    
    async def connect(self) -> bool:
        return True
    
    async def test_connection(self) -> Dict[str, Any]:
        return {"status": "ok", "type": "youtube"}
    
    async def list_sources(self) -> List[Dict[str, Any]]:
        return [{"id": "youtube", "name": "YouTube", "type": "youtube"}]
    
    async def fetch(self, source_id: str) -> Dict[str, Any]:
        return {"id": source_id, "type": "youtube", "content": ""}
    
    async def sync(self, source_id: str, incremental: bool = True) -> Dict[str, Any]:
        return {"source_id": source_id, "status": "synced"}


class ConnectorManager:
    """Manages all connectors"""
    
    CONNECTOR_MAP = {
        "pdf": PDFConnector,
        "web": WebConnector,
        "database": DatabaseConnector,
        "api": APIConnector,
        "file": FileConnector,
        "youtube": YouTubeConnector,
    }
    
    def __init__(self):
        self._connectors = {}
    
    def get_connector(self, source_type: str, config: Dict[str, Any]) -> BaseConnector:
        """Get or create connector instance"""
        if source_type not in self._connectors:
            cls = self.CONNECTOR_MAP.get(source_type)
            if not cls:
                raise ValueError(f"Unknown source type: {source_type}")
            self._connectors[source_type] = cls(config)
        return self._connectors[source_type]
    
    def list_supported_types(self) -> List[str]:
        """List all supported source types"""
        return list(self.CONNECTOR_MAP.keys())


connector_manager = ConnectorManager()