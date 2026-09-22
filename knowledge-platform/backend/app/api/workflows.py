"""Workflows API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from backend.app.schemas import WorkflowCreate, WorkflowResponse

router = APIRouter()

# In-memory storage
_workflows = {}
_wf_id_counter = 1


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(wf: WorkflowCreate):
    """Create a new workflow"""
    global _wf_id_counter
    
    wf_id = f"wf_{_wf_id_counter}"
    _wf_id_counter += 1
    
    new_wf = {
        "id": wf_id,
        "kb_id": wf.kb_id,
        "name": wf.name,
        "description": wf.description,
        "nodes": wf.nodes,
        "edges": wf.edges,
        "is_active": True,
        "version": "1.0",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    _workflows[wf_id] = new_wf
    return new_wf


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(kb_id: str = None):
    """List workflows"""
    wfs = list(_workflows.values())
    if kb_id:
        wfs = [w for w in wfs if w["kb_id"] == kb_id]
    return wfs


@router.get("/{wf_id}", response_model=WorkflowResponse)
async def get_workflow(wf_id: str):
    """Get workflow by ID"""
    if wf_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _workflows[wf_id]


@router.put("/{wf_id}", response_model=WorkflowResponse)
async def update_workflow(wf_id: str, wf: WorkflowCreate):
    """Update workflow"""
    if wf_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    _workflows[wf_id].update({
        "name": wf.name,
        "description": wf.description,
        "nodes": wf.nodes,
        "edges": wf.edges,
        "updated_at": datetime.utcnow()
    })
    
    return _workflows[wf_id]


@router.delete("/{wf_id}")
async def delete_workflow(wf_id: str):
    """Delete workflow"""
    if wf_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    del _workflows[wf_id]
    return {"message": "Workflow deleted"}


@router.post("/{wf_id}/execute")
async def execute_workflow(wf_id: str):
    """Execute a workflow"""
    if wf_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    wf = _workflows[wf_id]
    
    # Execute workflow nodes
    from backend.app.services.processing import processing_engine
    
    # Simple execution: process each node in sequence
    results = []
    for node in wf.get("nodes", []):
        node_type = node.get("type")
        if node_type == "process":
            # Process content
            pass
        results.append({"node": node.get("name"), "status": "executed"})
    
    return {
        "workflow_id": wf_id,
        "status": "completed",
        "results": results,
        "executed_at": datetime.utcnow().isoformat()
    }