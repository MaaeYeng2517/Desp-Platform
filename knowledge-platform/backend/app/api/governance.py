"""Governance API endpoints"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()


@router.get("/permissions")
async def get_permissions():
    """Get available permissions"""
    from backend.app.services.governance import governance
    
    return {
        "permissions": [p.value for p in governance.roles.keys()]
    }


@router.get("/roles")
async def get_roles():
    """Get available roles"""
    from backend.app.services.governance import governance
    
    return {
        "roles": [
            {
                "name": role.value,
                "permissions": [p.value for p in permissions]
            }
            for role, permissions in governance.roles.items()
        ]
    }


@router.post("/policies")
async def create_policy(name: str, rules: dict):
    """Create a governance policy"""
    from backend.app.services.governance import governance
    
    governance.policy.define_policy(name, rules)
    
    return {
        "name": name,
        "rules": rules,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/audit")
async def get_audit_logs(user_id: str = None, limit: int = 100):
    """Get audit logs"""
    from backend.app.services.governance import governance
    
    logs = governance.audit.get_logs(user_id=user_id, limit=limit)
    
    return {
        "logs": logs,
        "total": len(logs)
    }


@router.post("/approvals")
async def submit_approval(kb_id: str, document_id: str, creator_id: str, reviewers: List[str]):
    """Submit document for approval"""
    from backend.app.services.governance import governance
    
    approval = governance.approval.submit_for_approval(
        kb_id, document_id, creator_id, reviewers
    )
    
    return approval


@router.post("/approvals/{approval_id}/approve")
async def approve_document(approval_id: str, reviewer_id: str, comments: str = ""):
    """Approve a document"""
    from backend.app.services.governance import governance
    
    result = governance.approval.approve(approval_id, reviewer_id, comments)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result