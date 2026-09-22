"""Ingestion engine for processing documents"""
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class IngestionEngine:
    """Handles document ingestion from various sources"""
    
    def __init__(self):
        self.processors = {}
    
    def register_processor(self, source_type: str, processor):
        """Register a processor for a source type"""
        self.processors[source_type] = processor
    
    async def ingest(self, source_type: str, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest a document from source"""
        logger.info(f"Ingesting from {source_type}")
        
        processor = self.processors.get(source_type)
        if not processor:
            raise ValueError(f"No processor for {source_type}")
        
        result = await processor.process(source_config)
        result["checksum"] = self._generate_checksum(result.get("content", ""))
        result["ingested_at"] = datetime.utcnow().isoformat()
        
        return result
    
    async def incremental_sync(self, source_type: str, source_config: Dict[str, Any], 
                               last_checksum: Optional[str] = None) -> Dict[str, Any]:
        """Perform incremental sync with change detection"""
        result = await self.ingest(source_type, source_config)
        new_checksum = result["checksum"]
        
        if last_checksum and new_checksum == last_checksum:
            result["changed"] = False
            result["action"] = "skipped"
        else:
            result["changed"] = True
            result["action"] = "processed"
        
        return result
    
    def _generate_checksum(self, content: str) -> str:
        """Generate SHA256 checksum"""
        return hashlib.sha256(content.encode()).hexdigest()


class PDFProcessor:
    """Processor for PDF documents"""
    
    async def process(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "pdf",
            "content": "PDF content extracted",
            "metadata": {"pages": 1},
            "source": config
        }


class WebProcessor:
    """Processor for web pages"""
    
    async def process(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "web",
            "content": "Web content extracted",
            "metadata": {"url": config.get("url", "")},
            "source": config
        }


class FileProcessor:
    """Processor for uploaded files"""
    
    async def process(self, config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "file",
            "content": "File content extracted",
            "metadata": {"filename": config.get("filename", "")},
            "source": config
        }


# Initialize ingestion engine
ingestion_engine = IngestionEngine()
ingestion_engine.register_processor("pdf", PDFProcessor())
ingestion_engine.register_processor("web", WebProcessor())
ingestion_engine.register_processor("file", FileProcessor())