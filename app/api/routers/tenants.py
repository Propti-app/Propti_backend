from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ... import schemas, crud, models
from ...database import get_db
from ...utils.auth import get_current_landlord_id

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("/{tenant_id}", response_model=schemas.TenantResponse)
def get_tenant_details(
    tenant_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    """Get tenant details with room info"""
    tenant = db.query(models.Tenant).filter(
        models.Tenant.tenant_id == tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Verify tenant belongs to landlord's property
    if tenant.assigned_room_id:
        room = db.query(models.Room).join(
            models.Property, models.Room.property_id == models.Property.property_id
        ).filter(
            models.Room.room_id == tenant.assigned_room_id,
            models.Property.landlord_id == landlord_id
        ).first()
        if not room:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    return tenant


#new router to get all tenants for landlord
@router.get("/", response_model=list[schemas.TenantResponse])
def get_tenants(
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    # Get all tenants whose rooms belong to landlord's properties
    tenants = db.query(models.Tenant).join(
        models.Room, 
        models.Tenant.assigned_room_id == models.Room.room_id,
        isouter=True  # Left join to include tenants without rooms
    ).join(
        models.Property, 
        models.Room.property_id == models.Property.property_id,
        isouter=True
    ).filter(
        (models.Property.landlord_id == landlord_id) | 
        (models.Tenant.assigned_room_id == None)  # Include unassigned tenants
    ).offset(skip).limit(limit).all()
    
    return tenants

@router.post("/", response_model=schemas.TenantResponse)
def create_tenant(
    tenant: schemas.TenantCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    return crud.create_tenant(db, tenant)

@router.post("/{tenant_id}/assign-room", response_model=schemas.TenantResponse)
def assign_tenant_to_room(
    tenant_id: int,
    room_id: int,
    rent_amount: float,
    due_date: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    # Verify room belongs to landlord
    room = db.query(models.Room).join(
        models.Property, models.Room.property_id == models.Property.property_id
    ).filter(
        models.Room.room_id == room_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not room:
        raise HTTPException(status_code=403, detail="Not authorized to assign tenant to this room")
    tenant = crud.assign_tenant_to_room(db, tenant_id, room_id, rent_amount, due_date)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant or room not found")
    return tenant

@router.post("/{tenant_id}/deactivate", response_model=schemas.TenantResponse)
def deactivate_tenant(
    tenant_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    tenant = crud.deactivate_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.post("/{tenant_id}/vacate", response_model=schemas.ArchivedTenantResponse)
def vacate_and_archive_tenant(
    tenant_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    tenant = db.query(models.Tenant).filter(models.Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    # Verify tenant's room (if assigned) belongs to landlord
    if tenant.assigned_room_id:
        room = db.query(models.Room).join(
            models.Property, models.Room.property_id == models.Property.property_id
        ).filter(
            models.Room.room_id == tenant.assigned_room_id,
            models.Property.landlord_id == landlord_id
        ).first()
        if not room:
            raise HTTPException(status_code=403, detail="Not authorized to vacate this tenant")
    archived = crud.vacate_and_archive_tenant(db, tenant_id)
    if not archived:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return archived


