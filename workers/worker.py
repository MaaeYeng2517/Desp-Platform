"""Background worker for processing tasks"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

from backend.app.services.ingestion import ingestion_engine
from backend.app.services.processing import processing_engine
from backend.app.services.indexing import hybrid_index

logger = logging.getLogger(__name__)


class TaskQueue:
    """Simple in-memory task queue"""
    
    def __init__(self):
        self.tasks = []
        self.running = False
    
    async def enqueue(self, task_type: str, data: Dict[str, Any]):
        """Add task to queue"""
        self.tasks.append({
            "type": task_type,
            "data": data,
            "created_at": datetime.utcnow()
        })
        logger.info(f"Enqueued task: {task_type}")
    
    async def process_next(self):
        """Process next task in queue"""
        if not self.tasks:
            return None
        
        task = self.tasks.pop(0)
        
        try:
            if task["type"] == "ingest":
                result = await self._process_ingest(task["data"])
            elif task["type"] == "process":
                result = await self._process_process(task["data"])
            elif task["type"] == "index":
                result = await self._process_index(task["data"])
            else:
                result = {"error": f"Unknown task type: {task['type']}"}
            
            task["result"] = result
            task["completed_at"] = datetime.utcnow()
            return task
        except Exception as e:
            task["error"] = str(e)
            task["completed_at"] = datetime.utcnow()
            return task
    
    async def _process_ingest(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ingestion task"""
        source_type = data.get("source_type")
        config = data.get("config", {})
        
        result = await ingestion_engine.ingest(source_type, config)
        return result
    
    async def _process_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process document processing task"""
        content = data.get("content", "")
        source_type = data.get("source_type", "file")
        chunk_size = data.get("chunk_size", 800)
        chunk_overlap = data.get("chunk_overlap", 100)
        
        result = await processing_engine.process(content, source_type, chunk_size, chunk_overlap)
        return result
    
    async def _process_index(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process indexing task"""
        doc_id = data.get("doc_id")
        content = data.get("content", "")
        metadata = data.get("metadata", {})
        
        hybrid_index.index(doc_id, content, metadata)
        
        return {
            "doc_id": doc_id,
            "status": "indexed",
            "indexed_at": datetime.utcnow().isoformat()
        }


# Global task queue
task_queue = TaskQueue()


async def worker_loop():
    """Main worker loop"""
    logger.info("Worker started")
    
    while True:
        try:
            result = await task_queue.process_next()
            if result:
                logger.info(f"Task completed: {result['type']}")
            else:
                await asyncio.sleep(1)  # Wait if no tasks
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(5)


async def start_worker():
    """Start the worker"""
    await worker_loop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_worker())