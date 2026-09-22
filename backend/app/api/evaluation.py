"""Evaluation API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from backend.app.schemas import EvaluationRequest, EvaluationResponse

router = APIRouter()


@router.post("/", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """Run evaluation on knowledge base"""
    from backend.app.services.evaluation import evaluation_engine
    
    result = await evaluation_engine.evaluate(
        str(request.kb_id),
        str(request.dataset_id) if request.dataset_id else None,
        request.questions
    )
    
    return {
        "run_id": f"run_{datetime.utcnow().timestamp()}",
        "metrics": result["metrics"],
        "overall_score": result["metrics"]["overall_score"],
        "results": result["results"],
        "status": "completed"
    }


@router.post("/datasets")
async def create_dataset(kb_id: str, name: str, questions: List[dict]):
    """Create evaluation dataset"""
    from backend.app.services.evaluation import evaluation_engine
    
    dataset_id = f"ds_{datetime.utcnow().timestamp()}"
    evaluation_engine.register_dataset(dataset_id, questions)
    
    return {
        "dataset_id": dataset_id,
        "kb_id": kb_id,
        "name": name,
        "question_count": len(questions)
    }


@router.get("/datasets")
async def list_datasets():
    """List evaluation datasets"""
    from backend.app.services.evaluation import evaluation_engine
    
    return {
        "datasets": list(evaluation_engine.datasets.keys())
    }