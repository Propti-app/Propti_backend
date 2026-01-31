# app/api/routers/tenants.py
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
    """Get all active tenants for the landlord with room information"""
    tenants = crud.get_tenants(db, landlord_id=landlord.landlord_id, skip=skip, limit=limit)
    return tenants


@router.get("/{tenant_id}")
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get tenant details with room information"""
    tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Verify tenant belongs to landlord
    if tenant["landlord_id"] != landlord.landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
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
    tenant_data: schemas.TenantCreate,  # Use TenantCreate since all fields are optional anyway
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Update tenant information"""
    # Get tenant and verify ownership
    tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["landlord_id"] != landlord.landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update tenant with provided fields
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
    """Assign a tenant to a room"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["landlord_id"] != landlord.landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
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
    """Vacate and archive a tenant"""
    # Verify tenant belongs to landlord
    tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["landlord_id"] != landlord.landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        archived = crud.vacate_and_archive_tenant(db, tenant_id=tenant_id)
        return {
            "message": "Tenant vacated successfully",
            "archived_tenant": {
                "archived_id": archived.archived_id,
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
            "archived_id": tenant.archived_id,
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
    """Deactivate a tenant (soft delete)"""
    tenant = crud.get_tenant(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if tenant["landlord_id"] != landlord.landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        deactivated_tenant = crud.deactivate_tenant(db, tenant_id=tenant_id)
        return {"message": "Tenant deactivated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))












# # app/api/routers/tenants.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from app import crud, schemas
# from app.database import get_db
# from app.utils.auth import get_current_landlord

# router = APIRouter(prefix="/tenants", tags=["tenants"])


# @router.get("/", response_model=List[schemas.TenantResponse])
# def list_tenants(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get all active tenants for the landlord with room information"""
#     tenants = crud.get_tenants(db, landlord_id=landlord.landlord_id, skip=skip, limit=limit)
#     return tenants


# @router.get("/{tenant_id}")
# def get_tenant(
#     tenant_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get tenant details with room information"""
#     tenant = crud.get_tenant(db, tenant_id=tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     # Verify tenant belongs to landlord
#     if tenant["landlord_id"] != landlord.landlord_id:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     return tenant


# @router.post("/", response_model=schemas.TenantResponse)
# def create_tenant(
#     tenant: schemas.TenantCreate,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Create a new tenant"""
#     try:
#         db_tenant = crud.create_tenant(db, tenant=tenant, landlord_id=landlord.landlord_id)
#         return db_tenant
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.put("/{tenant_id}")
# def update_tenant(
#     tenant_id: int,
#     tenant_data: schemas.TenantCreate,  # Use TenantCreate since all fields are optional anyway
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Update tenant information"""
#     # Get tenant and verify ownership
#     tenant = crud.get_tenant(db, tenant_id=tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     if tenant["landlord_id"] != landlord.landlord_id:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     # Update tenant with provided fields
#     update_data = tenant_data.dict(exclude_unset=True)
#     try:
#         updated_tenant = crud.update_tenant(db, tenant_id=tenant_id, **update_data)
#         return updated_tenant
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/{tenant_id}/assign-room")
# def assign_tenant_to_room(
#     tenant_id: int,
#     room_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Assign a tenant to a room"""
#     # Verify tenant belongs to landlord
#     tenant = crud.get_tenant(db, tenant_id=tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     if tenant["landlord_id"] != landlord.landlord_id:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     try:
#         updated_tenant = crud.assign_tenant_to_room(db, tenant_id=tenant_id, room_id=room_id)
#         return updated_tenant
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/{tenant_id}/vacate")
# def vacate_tenant(
#     tenant_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Vacate and archive a tenant"""
#     # Verify tenant belongs to landlord
#     tenant = crud.get_tenant(db, tenant_id=tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     if tenant["landlord_id"] != landlord.landlord_id:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     try:
#         archived = crud.vacate_and_archive_tenant(db, tenant_id=tenant_id)
#         return {
#             "message": "Tenant vacated successfully",
#             "archived_tenant": {
#                 "archived_id": archived.archived_id,
#                 "full_name": archived.full_name,
#                 "phone_number": archived.phone_number,
#                 "archived_at": archived.archived_at
#             }
#         }
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/archived/list")
# def get_archived_tenants(
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get all archived tenants for the landlord"""
#     archived = crud.get_archived_tenants(db, landlord_id=landlord.landlord_id)
    
#     result = []
#     for tenant in archived:
#         result.append({
#             "archived_id": tenant.archived_id,
#             "original_tenant_id": tenant.original_tenant_id,
#             "full_name": tenant.full_name,
#             "phone_number": tenant.phone_number,
#             "email": tenant.email,
#             "room_number": tenant.room_number,
#             "final_balance": tenant.final_balance,
#             "archived_at": tenant.archived_at
#         })
    
#     return {"archived_tenants": result}


# @router.delete("/{tenant_id}")
# def deactivate_tenant(
#     tenant_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Deactivate a tenant (soft delete)"""
#     tenant = crud.get_tenant(db, tenant_id=tenant_id)
#     if not tenant:
#         raise HTTPException(status_code=404, detail="Tenant not found")
    
#     if tenant["landlord_id"] != landlord.landlord_id:
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     try:
#         deactivated_tenant = crud.deactivate_tenant(db, tenant_id=tenant_id)
#         return {"message": "Tenant deactivated successfully"}
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))








# # # app/api/routers/tenants.py
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from typing import List
# # from app import crud, schemas
# # from app.database import get_db
# # from app.utils.auth import get_current_landlord
# # router = APIRouter(prefix="/tenants", tags=["tenants"])


# # @router.get("/", response_model=List[schemas.TenantResponse])
# # def list_tenants(
# #     skip: int = 0,
# #     limit: int = 100,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get all active tenants for the landlord with room information"""
# #     tenants = crud.get_tenants(db, landlord_id=landlord.landlord_id, skip=skip, limit=limit)
# #     return tenants


# # @router.get("/{tenant_id}")
# # def get_tenant(
# #     tenant_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get tenant details with room information"""
# #     tenant = crud.get_tenant(db, tenant_id=tenant_id)
# #     if not tenant:
# #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# #     # Verify tenant belongs to landlord
# #     if tenant["landlord_id"] != landlord.landlord_id:
# #         raise HTTPException(status_code=403, detail="Not authorized")
    
# #     return tenant


# # @router.post("/", response_model=schemas.TenantResponse)
# # def create_tenant(
# #     tenant: schemas.TenantCreate,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Create a new tenant"""
# #     try:
# #         db_tenant = crud.create_tenant(db, tenant=tenant, landlord_id=landlord.landlord_id)
# #         return db_tenant
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.put("/{tenant_id}")
# # def update_tenant(
# #     tenant_id: int,
# #     tenant_data: schemas.TenantCreate,  # Use TenantCreate since all fields are optional anyway
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Update tenant information"""
# #     # Get tenant and verify ownership
# #     tenant = crud.get_tenant(db, tenant_id=tenant_id)
# #     if not tenant:
# #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# #     if tenant["landlord_id"] != landlord.landlord_id:
# #         raise HTTPException(status_code=403, detail="Not authorized")
    
# #     # Update tenant with provided fields
# #     update_data = tenant_data.dict(exclude_unset=True)
# #     try:
# #         updated_tenant = crud.update_tenant(db, tenant_id=tenant_id, **update_data)
# #         return updated_tenant
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.post("/{tenant_id}/assign-room")
# # def assign_tenant_to_room(
# #     tenant_id: int,
# #     room_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Assign a tenant to a room"""
# #     # Verify tenant belongs to landlord
# #     tenant = crud.get_tenant(db, tenant_id=tenant_id)
# #     if not tenant:
# #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# #     if tenant["landlord_id"] != landlord.landlord_id:
# #         raise HTTPException(status_code=403, detail="Not authorized")
    
# #     try:
# #         updated_tenant = crud.assign_tenant_to_room(db, tenant_id=tenant_id, room_id=room_id)
# #         return updated_tenant
# #     except ValueError as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.post("/{tenant_id}/vacate")
# # def vacate_tenant(
# #     tenant_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Vacate and archive a tenant"""
# #     # Verify tenant belongs to landlord
# #     tenant = crud.get_tenant(db, tenant_id=tenant_id)
# #     if not tenant:
# #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# #     if tenant["landlord_id"] != landlord.landlord_id:
# #         raise HTTPException(status_code=403, detail="Not authorized")
    
# #     try:
# #         archived = crud.vacate_and_archive_tenant(db, tenant_id=tenant_id)
# #         return {
# #             "message": "Tenant vacated successfully",
# #             "archived_tenant": {
# #                 "archived_id": archived.archived_id,
# #                 "full_name": archived.full_name,
# #                 "phone_number": archived.phone_number,
# #                 "archived_at": archived.archived_at
# #             }
# #         }
# #     except ValueError as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.get("/archived/list")
# # def get_archived_tenants(
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get all archived tenants for the landlord"""
# #     archived = crud.get_archived_tenants(db, landlord_id=landlord.landlord_id)
    
# #     result = []
# #     for tenant in archived:
# #         result.append({
# #             "archived_id": tenant.archived_id,
# #             "original_tenant_id": tenant.original_tenant_id,
# #             "full_name": tenant.full_name,
# #             "phone_number": tenant.phone_number,
# #             "email": tenant.email,
# #             "room_number": tenant.room_number,
# #             "final_balance": tenant.final_balance,
# #             "archived_at": tenant.archived_at
# #         })
    
# #     return {"archived_tenants": result}


# # @router.delete("/{tenant_id}")
# # def deactivate_tenant(
# #     tenant_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Deactivate a tenant (soft delete)"""
# #     tenant = crud.get_tenant(db, tenant_id=tenant_id)
# #     if not tenant:
# #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# #     if tenant["landlord_id"] != landlord.landlord_id:
# #         raise HTTPException(status_code=403, detail="Not authorized")
    
# #     try:
# #         deactivated_tenant = crud.deactivate_tenant(db, tenant_id=tenant_id)
# #         return {"message": "Tenant deactivated successfully"}
# #     except ValueError as e:
# #         raise HTTPException(status_code=400, detail=str(e))





# # # # app/api/routers/tenants.py - ENHANCED VERSION
# # # from fastapi import APIRouter, Depends, HTTPException
# # # from sqlalchemy.orm import Session
# # # from ... import schemas, crud, models
# # # from ...database import get_db
# # # from ...utils.auth import get_current_landlord_id

# # # router = APIRouter(prefix="/tenants", tags=["Tenants"])


# # # @router.post("/", response_model=schemas.TenantResponse)
# # # def create_tenant(
# # #     tenant: schemas.TenantCreate,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """Create a new tenant"""
# # #     return crud.create_tenant(db, tenant)


# # # @router.get("/", response_model=list[schemas.TenantResponse])
# # # def get_all_tenants(
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db),
# # #     skip: int = 0,
# # #     limit: int = 100
# # # ):
# # #     """Get all active tenants for the landlord"""
# # #     tenants = db.query(models.Tenant).join(
# # #         models.Room, models.Tenant.assigned_room_id == models.Room.room_id, isouter=True
# # #     ).join(
# # #         models.Property, models.Room.property_id == models.Property.property_id, isouter=True
# # #     ).filter(
# # #         models.Tenant.is_active == True
# # #     ).offset(skip).limit(limit).all()
    
# # #     # Enrich with room_number for display
# # #     result = []
# # #     for tenant in tenants:
# # #         tenant_dict = {
# # #             'tenant_id': tenant.tenant_id,
# # #             'full_name': tenant.full_name,
# # #             'phone_number': tenant.phone_number,
# # #             'email': tenant.email,
# # #             'faculty': tenant.faculty,
# # #             'year_of_study': tenant.year_of_study,
# # #             'guardian_phone_number': tenant.guardian_phone_number,
# # #             'guardian_name': tenant.guardian_name,
# # #             'guardian_location': tenant.guardian_location,
# # #             'photo': tenant.photo,
# # #             'id_card_number': tenant.id_card_number,
# # #             'assigned_room_id': tenant.assigned_room_id,
# # #             'balance': tenant.balance,
# # #             'created_at': tenant.created_at,
# # #             'updated_at': tenant.updated_at,
# # #             'is_active': tenant.is_active,
# # #             'room_number': tenant.assigned_room.room_number if tenant.assigned_room else None
# # #         }
# # #         result.append(tenant_dict)
    
# # #     return result


# # # @router.get("/{tenant_id}", response_model=schemas.TenantResponse)
# # # def get_tenant_details(
# # #     tenant_id: int,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """Get detailed tenant information"""
# # #     tenant = db.query(models.Tenant).filter(
# # #         models.Tenant.tenant_id == tenant_id
# # #     ).first()
    
# # #     if not tenant:
# # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # #     # Add room_number to response
# # #     tenant_dict = {
# # #         'tenant_id': tenant.tenant_id,
# # #         'full_name': tenant.full_name,
# # #         'phone_number': tenant.phone_number,
# # #         'email': tenant.email,
# # #         'faculty': tenant.faculty,
# # #         'year_of_study': tenant.year_of_study,
# # #         'guardian_phone_number': tenant.guardian_phone_number,
# # #         'guardian_name': tenant.guardian_name,
# # #         'guardian_location': tenant.guardian_location,
# # #         'photo': tenant.photo,
# # #         'id_card_number': tenant.id_card_number,
# # #         'assigned_room_id': tenant.assigned_room_id,
# # #         'balance': tenant.balance,
# # #         'created_at': tenant.created_at,
# # #         'updated_at': tenant.updated_at,
# # #         'is_active': tenant.is_active,
# # #         'room_number': tenant.assigned_room.room_number if tenant.assigned_room else None
# # #     }
    
# # #     return tenant_dict


# # # @router.put("/{tenant_id}", response_model=schemas.TenantResponse)
# # # def update_tenant(
# # #     tenant_id: int,
# # #     tenant_update: schemas.TenantCreate,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """Update tenant information"""
# # #     db_tenant = db.query(models.Tenant).filter(
# # #         models.Tenant.tenant_id == tenant_id
# # #     ).first()
    
# # #     if not db_tenant:
# # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # #     # Update fields
# # #     for key, value in tenant_update.dict(exclude_unset=True).items():
# # #         setattr(db_tenant, key, value)
    
# # #     db.commit()
# # #     db.refresh(db_tenant)
    
# # #     return db_tenant


# # # @router.post("/{tenant_id}/assign-room", response_model=schemas.TenantResponse)
# # # def assign_tenant_to_room(
# # #     tenant_id: int,
# # #     room_id: int,
# # #     rent_amount: float,
# # #     due_date: int,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """Assign or reassign tenant to a room"""
# # #     # Verify room belongs to landlord
# # #     room = db.query(models.Room).join(
# # #         models.Property, models.Room.property_id == models.Property.property_id
# # #     ).filter(
# # #         models.Room.room_id == room_id,
# # #         models.Property.landlord_id == landlord_id
# # #     ).first()
    
# # #     if not room:
# # #         raise HTTPException(status_code=403, detail="Not authorized to assign to this room")
    
# # #     # Check if room is vacant
# # #     existing_tenant = db.query(models.Tenant).filter(
# # #         models.Tenant.assigned_room_id == room_id,
# # #         models.Tenant.is_active == True,
# # #         models.Tenant.tenant_id != tenant_id  # Allow reassigning same tenant
# # #     ).first()
    
# # #     if existing_tenant:
# # #         raise HTTPException(status_code=400, detail="Room is already occupied")
    
# # #     # Assign tenant
# # #     db_tenant = crud.assign_tenant_to_room(db, tenant_id, room_id, rent_amount, due_date)
    
# # #     if not db_tenant:
# # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # #     return db_tenant


# # # @router.post("/{tenant_id}/vacate", response_model=schemas.ArchivedTenantResponse)
# # # def vacate_tenant(
# # #     tenant_id: int,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """
# # #     Vacate tenant from room and archive their records
# # #     This preserves payment history and tenant data
# # #     """
# # #     # Verify tenant belongs to landlord's property
# # #     tenant = db.query(models.Tenant).join(
# # #         models.Room, models.Tenant.assigned_room_id == models.Room.room_id, isouter=True
# # #     ).join(
# # #         models.Property, models.Room.property_id == models.Property.property_id, isouter=True
# # #     ).filter(
# # #         models.Tenant.tenant_id == tenant_id
# # #     ).first()
    
# # #     if not tenant:
# # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # #     # Archive and vacate
# # #     archived = crud.vacate_and_archive_tenant(db, tenant_id)
    
# # #     if not archived:
# # #         raise HTTPException(status_code=404, detail="Failed to vacate tenant")
    
# # #     return archived


# # # @router.post("/{tenant_id}/deactivate", response_model=schemas.TenantResponse)
# # # def deactivate_tenant(
# # #     tenant_id: int,
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """Deactivate tenant without archiving (soft delete)"""
# # #     db_tenant = crud.deactivate_tenant(db, tenant_id)
    
# # #     if not db_tenant:
# # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # #     return db_tenant


# # # @router.get("/archived/list")
# # # def get_archived_tenants(
# # #     landlord_id: int = Depends(get_current_landlord_id),
# # #     db: Session = Depends(get_db),
# # #     skip: int = 0,
# # #     limit: int = 100
# # # ):
# # #     """Get list of archived tenants"""
# # #     from ...crud.report import get_archived_tenants
    
# # #     archived = get_archived_tenants(db, landlord_id, skip, limit)
# # #     return {"archived_tenants": archived}






# # # # from fastapi import APIRouter, Depends, HTTPException
# # # # from sqlalchemy.orm import Session
# # # # from ... import schemas, crud, models
# # # # from ...database import get_db
# # # # from ...utils.auth import get_current_landlord_id

# # # # router = APIRouter(prefix="/tenants", tags=["Tenants"])

# # # # @router.get("/{tenant_id}", response_model=schemas.TenantResponse)
# # # # def get_tenant_details(
# # # #     tenant_id: int,
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db)
# # # # ):
# # # #     """Get tenant details with room info"""
# # # #     tenant = db.query(models.Tenant).filter(
# # # #         models.Tenant.tenant_id == tenant_id
# # # #     ).first()
    
# # # #     if not tenant:
# # # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # # #     # Verify tenant belongs to landlord's property
# # # #     if tenant.assigned_room_id:
# # # #         room = db.query(models.Room).join(
# # # #             models.Property, models.Room.property_id == models.Property.property_id
# # # #         ).filter(
# # # #             models.Room.room_id == tenant.assigned_room_id,
# # # #             models.Property.landlord_id == landlord_id
# # # #         ).first()
# # # #         if not room:
# # # #             raise HTTPException(status_code=403, detail="Not authorized")
    
# # # #     return tenant


# # # # #new router to get all tenants for landlord
# # # # @router.get("/", response_model=list[schemas.TenantResponse])
# # # # def get_tenants(
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db),
# # # #     skip: int = 0,
# # # #     limit: int = 100
# # # # ):
# # # #     # Get all tenants whose rooms belong to landlord's properties
# # # #     tenants = db.query(models.Tenant).join(
# # # #         models.Room, 
# # # #         models.Tenant.assigned_room_id == models.Room.room_id,
# # # #         isouter=True  # Left join to include tenants without rooms
# # # #     ).join(
# # # #         models.Property, 
# # # #         models.Room.property_id == models.Property.property_id,
# # # #         isouter=True
# # # #     ).filter(
# # # #         (models.Property.landlord_id == landlord_id) | 
# # # #         (models.Tenant.assigned_room_id == None)  # Include unassigned tenants
# # # #     ).offset(skip).limit(limit).all()
    
# # # #     return tenants

# # # # @router.post("/", response_model=schemas.TenantResponse)
# # # # def create_tenant(
# # # #     tenant: schemas.TenantCreate,
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db)
# # # # ):
# # # #     return crud.create_tenant(db, tenant)

# # # # @router.post("/{tenant_id}/assign-room", response_model=schemas.TenantResponse)
# # # # def assign_tenant_to_room(
# # # #     tenant_id: int,
# # # #     room_id: int,
# # # #     rent_amount: float,
# # # #     due_date: int,
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db)
# # # # ):
# # # #     # Verify room belongs to landlord
# # # #     room = db.query(models.Room).join(
# # # #         models.Property, models.Room.property_id == models.Property.property_id
# # # #     ).filter(
# # # #         models.Room.room_id == room_id,
# # # #         models.Property.landlord_id == landlord_id
# # # #     ).first()
# # # #     if not room:
# # # #         raise HTTPException(status_code=403, detail="Not authorized to assign tenant to this room")
# # # #     tenant = crud.assign_tenant_to_room(db, tenant_id, room_id, rent_amount, due_date)
# # # #     if not tenant:
# # # #         raise HTTPException(status_code=404, detail="Tenant or room not found")
# # # #     return tenant

# # # # @router.post("/{tenant_id}/deactivate", response_model=schemas.TenantResponse)
# # # # def deactivate_tenant(
# # # #     tenant_id: int,
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db)
# # # # ):
# # # #     tenant = crud.deactivate_tenant(db, tenant_id)
# # # #     if not tenant:
# # # #         raise HTTPException(status_code=404, detail="Tenant not found")
# # # #     return tenant

# # # # @router.post("/{tenant_id}/vacate", response_model=schemas.ArchivedTenantResponse)
# # # # def vacate_and_archive_tenant(
# # # #     tenant_id: int,
# # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # #     db: Session = Depends(get_db)
# # # # ):
# # # #     tenant = db.query(models.Tenant).filter(models.Tenant.tenant_id == tenant_id).first()
# # # #     if not tenant:
# # # #         raise HTTPException(status_code=404, detail="Tenant not found")
# # # #     # Verify tenant's room (if assigned) belongs to landlord
# # # #     if tenant.assigned_room_id:
# # # #         room = db.query(models.Room).join(
# # # #             models.Property, models.Room.property_id == models.Property.property_id
# # # #         ).filter(
# # # #             models.Room.room_id == tenant.assigned_room_id,
# # # #             models.Property.landlord_id == landlord_id
# # # #         ).first()
# # # #         if not room:
# # # #             raise HTTPException(status_code=403, detail="Not authorized to vacate this tenant")
# # # #     archived = crud.vacate_and_archive_tenant(db, tenant_id)
# # # #     if not archived:
# # # #         raise HTTPException(status_code=404, detail="Tenant not found")
# # # #     return archived


