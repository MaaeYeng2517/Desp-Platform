"""Governance and security layer"""
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """RBAC permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    PUBLISH = "publish"
    APPROVE = "approve"


class Role(str, Enum):
    """User roles"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class Policy:
    """Policy engine for access control"""
    
    def __init__(self):
        self.policies: Dict[str, Dict] = {}
    
    def define_policy(self, name: str, rules: Dict[str, Any]):
        """Define a policy"""
        self.policies[name] = rules
    
    def check_permission(self, user_id: str, resource: str, 
                        action: str, context: Dict = None) -> bool:
        """Check if user has permission"""
        # Placeholder - in production, check against database
        return True


class AuditLog:
    """Audit logging for compliance"""
    
    def __init__(self):
        self.logs: List[Dict] = []
    
    def log(self, user_id: str, action: str, resource: str,
            details: Dict = None, ip_address: str = None):
        """Log an audit event"""
        self.logs.append({
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_logs(self, user_id: str = None, action: str = None,
                resource: str = None, limit: int = 100) -> List[Dict]:
        """Get audit logs with filters"""
        filtered = self.logs
        
        if user_id:
            filtered = [l for l in filtered if l["user_id"] == user_id]
        if action:
            filtered = [l for l in filtered if l["action"] == action]
        if resource:
            filtered = [l for l in filtered if l["resource"] == resource]
        
        return filtered[-limit:]


class ApprovalWorkflow:
    """Approval workflow for knowledge publishing"""
    
    def __init__(self):
        self.workflows: Dict[str, Dict] = {}
        self.pending_approvals: List[Dict] = []
    
    def create_workflow(self, kb_id: str, steps: List[Dict]) -> str:
        """Create approval workflow"""
        workflow_id = f"wf_{datetime.utcnow().timestamp()}"
        self.workflows[workflow_id] = {
            "kb_id": kb_id,
            "steps": steps,
            "created_at": datetime.utcnow().isoformat()
        }
        return workflow_id
    
    def submit_for_approval(self, kb_id: str, document_id: str,
                           creator_id: str, reviewers: List[str]) -> Dict:
        """Submit document for approval"""
        approval = {
            "id": f"apr_{datetime.utcnow().timestamp()}",
            "kb_id": kb_id,
            "document_id": document_id,
            "creator_id": creator_id,
            "reviewers": reviewers,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.pending_approvals.append(approval)
        return approval
    
    def approve(self, approval_id: str, reviewer_id: str, 
               comments: str = "") -> Dict:
        """Approve a document"""
        for approval in self.pending_approvals:
            if approval["id"] == approval_id:
                approval["status"] = "approved"
                approval["approved_by"] = reviewer_id
                approval["approved_at"] = datetime.utcnow().isoformat()
                approval["comments"] = comments
                return approval
        
        return {"error": "Approval not found"}


class GovernanceEngine:
    """Main governance engine"""
    
    def __init__(self):
        self.policy = Policy()
        self.audit = AuditLog()
        self.approval = ApprovalWorkflow()
        self.roles: Dict[str, List[Permission]] = {
            Role.SUPERADMIN: [p for p in Permission],
            Role.ADMIN: [p for p in Permission],
            Role.EDITOR: [Permission.READ, Permission.WRITE, Permission.PUBLISH],
            Role.REVIEWER: [Permission.READ, Permission.APPROVE],
            Role.VIEWER: [Permission.READ],
        }
    
    def get_user_permissions(self, user_roles: List[str]) -> List[Permission]:
        """Get permissions for user roles"""
        permissions = set()
        for role in user_roles:
            if role in self.roles:
                permissions.update(self.roles[role])
        return list(permissions)
    
    def check_access(self, user_id: str, user_roles: List[str],
                    resource: str, action: str) -> bool:
        """Check if user can access resource"""
        permissions = self.get_user_permissions(user_roles)
        action_perm = Permission(action.lower())
        
        return action_perm in permissions


# Global governance engine
governance = GovernanceEngine()