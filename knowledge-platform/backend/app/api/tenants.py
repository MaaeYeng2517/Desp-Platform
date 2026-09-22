"""Tenants API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.app.schemas import TenantCreate, TenantResponse

router = APIRouter()

# In-memory storage for demo
_tenants = {}
_tenant_id_counter = 1


@router.post("/", response_model=TenantResponse)
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant"""
    global _tenant_id_counter
    
    tenant_id = f"t_{_tenant_id_counter}"
    _tenant_id_counter += 1
    
    from datetime import datetime
    new_tenant = {
        "id": tenant_id,
        "name": tenant.name,
        "slug": tenant.slug,
        "description": tenant.description,
        "settings": tenant.settings,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    _tenants[tenant_id] = new_tenant
    return new_tenant


@router.get("/", response_model=List[TenantResponse])
async def list_tenants():
    """List all tenants"""
    return list(_tenants.values())


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """Get tenant by ID"""
    if tenant_id not in _tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return _tenants[tenant_id]


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, tenant: TenantCreate):
    """Update tenant"""
    if tenant_id not in _tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    from datetime import datetime
    _tenants[tenant_id].update({
        "name": tenant.name,
        "slug": tenant.slug,
        "description": tenant.description,
        "settings": tenant.settings,
        "updated_at": datetime.utcnow()
    })
    
    return _tenants[tenant_id]


@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str):
    """Delete tenant"""
    if tenant_id not in _tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    del _tenants[tenant_id]
    return {"message": "Tenant deleted"}