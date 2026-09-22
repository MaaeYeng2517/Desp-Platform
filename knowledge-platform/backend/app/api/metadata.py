"""Metadata API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from backend.app.schemas import MetadataSchemaCreate, MetadataSchemaResponse

router = APIRouter()

# In-memory storage
_schemas = {}
_schema_id_counter = 1


@router.post("/", response_model=MetadataSchemaResponse)
async def create_schema(schema: MetadataSchemaCreate):
    """Create a metadata schema"""
    global _schema_id_counter
    
    schema_id = f"ms_{_schema_id_counter}"
    _schema_id_counter += 1
    
    new_schema = {
        "id": schema_id,
        "kb_id": schema.kb_id,
        "name": schema.name,
        "description": schema.description,
        "fields": schema.fields,
        "taxonomy": schema.taxonomy,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    _schemas[schema_id] = new_schema
    return new_schema


@router.get("/", response_model=List[MetadataSchemaResponse])
async def list_schemas(kb_id: str = None):
    """List metadata schemas"""
    schemas = list(_schemas.values())
    if kb_id:
        schemas = [s for s in schemas if s["kb_id"] == kb_id]
    return schemas


@router.get("/{schema_id}", response_model=MetadataSchemaResponse)
async def get_schema(schema_id: str):
    """Get schema by ID"""
    if schema_id not in _schemas:
        raise HTTPException(status_code=404, detail="Schema not found")
    return _schemas[schema_id]


@router.put("/{schema_id}", response_model=MetadataSchemaResponse)
async def update_schema(schema_id: str, schema: MetadataSchemaCreate):
    """Update schema"""
    if schema_id not in _schemas:
        raise HTTPException(status_code=404, detail="Schema not found")
    
    _schemas[schema_id].update({
        "name": schema.name,
        "description": schema.description,
        "fields": schema.fields,
        "taxonomy": schema.taxonomy,
        "updated_at": datetime.utcnow()
    })
    
    return _schemas[schema_id]


@router.delete("/{schema_id}")
async def delete_schema(schema_id: str):
    """Delete schema"""
    if schema_id not in _schemas:
        raise HTTPException(status_code=404, detail="Schema not found")
    
    del _schemas[schema_id]
    return {"message": "Schema deleted"}


@router.post("/{schema_id}/validate")
async def validate_data(schema_id: str, data: dict):
    """Validate data against schema"""
    from backend.app.services.metadata import metadata_engine
    
    result = metadata_engine.validate(schema_id, data)
    return result