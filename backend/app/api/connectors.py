"""Connectors API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

router = APIRouter()


@router.get("/types")
async def get_connector_types():
    """Get supported connector types"""
    from backend.app.services.connectors import connector_manager
    
    return {
        "types": connector_manager.list_supported_types()
    }


@router.post("/test")
async def test_connection(source_type: str, config: dict):
    """Test a connector connection"""
    from backend.app.services.connectors import connector_manager
    
    try:
        connector = connector_manager.get_connector(source_type, config)
        result = await connector.test_connection()
        
        return {
            "source_type": source_type,
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "source_type": source_type,
            "status": "error",
            "error": str(e)
        }


@router.post("/sync")
async def sync_source(source_type: str, config: dict, source_id: str = None):
    """Sync from a source"""
    from backend.app.services.connectors import connector_manager
    from backend.app.services.ingestion import ingestion_engine
    
    try:
        connector = connector_manager.get_connector(source_type, config)
        
        # Test connection first
        test_result = await connector.test_connection()
        if test_result.get("status") != "ok":
            raise HTTPException(status_code=400, detail="Connection test failed")
        
        # Perform sync
        result = await connector.sync(source_id or "default", incremental=True)
        
        return {
            "source_type": source_type,
            "status": "success",
            "result": result,
            "synced_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def list_sources(source_type: str = None):
    """List available sources"""
    from backend.app.services.connectors import connector_manager
    
    if source_type:
        connector = connector_manager.get_connector(source_type, {})
        sources = await connector.list_sources()
    else:
        sources = []
        for st in connector_manager.list_supported_types():
            connector = connector_manager.get_connector(st, {})
            sources.extend(await connector.list_sources())
    
    return {
        "sources": sources
    }