# app/api/routers/tenants.py - PRODUCTION SECURE VERSION
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.utils.auth import get_current_landlord

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=List[schemas.TenantResponse])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get all active tenants for the landlord"""
    tenants = crud.get_tenants(db, landlord_id=landlord.landlord_id, skip=skip, limit=limit)
    return tenants


@router.get("/{tenant_id}")
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get tenant details - SECURE"""
    tenant = crud.get_tenant(db, tenant_id=tenant_id, landlord_id=landlord.landlord_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or not authorized")
    
    return tenant


@router.post("/", response_model=schemas.TenantResponse)
def create_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Create a new tenant"""
    try:
        db_tenant = crud.create_tenant(db, tenant=tenant, landlord_id=landlord.landlord_id)
        return db_tenant
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tenant_id}")
def update_tenant(
    tenant_id: int,
    tenant_data: schemas.TenantCreate,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Update tenant information - SECURE"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id, landlord_id=landlord.landlord_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or not authorized")
    
    update_data = tenant_data.dict(exclude_unset=True)
    try:
        updated_tenant = crud.update_tenant(db, tenant_id=tenant_id, **update_data)
        return updated_tenant
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{tenant_id}/assign-room")
def assign_tenant_to_room(
    tenant_id: int,
    room_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Assign a tenant to a room - SECURE"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id, landlord_id=landlord.landlord_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or not authorized")
    
    # Verify room belongs to landlord
    from app.models import Room, Property
    room = db.query(Room).join(Property).filter(
        Room.room_id == room_id,
        Property.landlord_id == landlord.landlord_id
    ).first()
    
    if not room:
        raise HTTPException(status_code=403, detail="Room not found or not authorized")
    
    try:
        updated_tenant = crud.assign_tenant_to_room(db, tenant_id=tenant_id, room_id=room_id)
        return updated_tenant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{tenant_id}/vacate")
def vacate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Vacate and archive a tenant - SECURE"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id, landlord_id=landlord.landlord_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or not authorized")
    
    try:
        archived = crud.vacate_and_archive_tenant(db, tenant_id=tenant_id)
        return {
            "message": "Tenant vacated successfully",
            "archived_tenant": {
                "archived_tenant_id": archived.archived_tenant_id,
                "full_name": archived.full_name,
                "phone_number": archived.phone_number,
                "archived_at": archived.archived_at
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/archived/list")
def get_archived_tenants(
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get all archived tenants for the landlord"""
    archived = crud.get_archived_tenants(db, landlord_id=landlord.landlord_id)
    
    result = []
    for tenant in archived:
        result.append({
            "archived_tenant_id": tenant.archived_tenant_id,
            "original_tenant_id": tenant.original_tenant_id,
            "full_name": tenant.full_name,
            "phone_number": tenant.phone_number,
            "email": tenant.email,
            "room_number": tenant.room_number,
            "final_balance": tenant.final_balance,
            "archived_at": tenant.archived_at
        })
    
    return {"archived_tenants": result}


@router.delete("/{tenant_id}")
def deactivate_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Deactivate a tenant (soft delete) - SECURE"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id, landlord_id=landlord.landlord_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found or not authorized")
    
    try:
        deactivated_tenant = crud.deactivate_tenant(db, tenant_id=tenant_id)
        return {"message": "Tenant deactivated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




