# app/crud/tenant.py - SIMPLIFIED VERSION
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Tenant, Room, Property, ArchivedTenant
from app.schemas import TenantCreate
from datetime import datetime

def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
    """Create a new tenant"""
    db_tenant = Tenant(
        landlord_id=landlord_id,
        full_name=tenant.full_name,
        phone_number=tenant.phone_number,
        email=tenant.email,
        id_card_number=tenant.id_card_number,
        faculty=tenant.faculty,
        year_of_study=tenant.year_of_study,
        guardian_name=tenant.guardian_name,
        guardian_phone=tenant.guardian_phone,
        guardian_location=tenant.guardian_location,
        is_active=True,
        balance=0.0
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def vacate_and_archive_tenant(db: Session, tenant_id: int):
    """Vacate tenant and archive their data"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    # Get room info before vacating
    room_info = None
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room_info = room.room_number
    
    # Create archived record - ONLY fields that exist in ArchivedTenant model
    db_archived = ArchivedTenant(
        original_tenant_id=db_tenant.tenant_id,
        landlord_id=db_tenant.landlord_id,
        full_name=db_tenant.full_name,
        phone_number=db_tenant.phone_number,
        email=db_tenant.email,
        room_number=room_info,
        final_balance=db_tenant.balance,
        archived_at=func.now()
    )
    
    db.add(db_archived)
    
    # Clear room assignment
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room.is_occupied = False
    
    db_tenant.assigned_room_id = None
    db_tenant.is_active = False
    
    db.commit()
    db.refresh(db_archived)
    
    return db_archived


def deactivate_tenant(db: Session, tenant_id: int):
    """Deactivate a tenant (existing function - keep as is)"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    db_tenant.is_active = False
    
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room.is_occupied = False
        db_tenant.assigned_room_id = None
    
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenant(db: Session, tenant_id: int):
    """Get tenant with room information"""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        return None
    
    # Convert to dict and add room_number if assigned
    tenant_dict = {
        "tenant_id": tenant.tenant_id,
        "landlord_id": tenant.landlord_id,
        "full_name": tenant.full_name,
        "phone_number": tenant.phone_number,
        "email": tenant.email,
        "id_card_number": tenant.id_card_number,
        "faculty": tenant.faculty,
        "year_of_study": tenant.year_of_study,
        "guardian_name": tenant.guardian_name,
        "guardian_phone": tenant.guardian_phone,
        "guardian_location": tenant.guardian_location,
        "assigned_room_id": tenant.assigned_room_id,
        "balance": tenant.balance,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at,
        "room_number": None,
        "property_name": None,
        "room_rent": None
    }
    
    # Get room details if assigned
    if tenant.assigned_room_id:
        room = db.query(Room).join(
            Property, Room.property_id == Property.property_id
        ).filter(Room.room_id == tenant.assigned_room_id).first()
        
        if room:
            tenant_dict["room_number"] = room.room_number
            tenant_dict["room_rent"] = room.rent_amount
            tenant_dict["property_name"] = room.property.property_name if room.property else None
    
    return tenant_dict


def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    """Get all active tenants for a landlord with room info"""
    tenants = db.query(Tenant).filter(
        Tenant.landlord_id == landlord_id,
        Tenant.is_active == True
    ).offset(skip).limit(limit).all()
    
    result = []
    for tenant in tenants:
        tenant_data = {
            "tenant_id": tenant.tenant_id,
            "full_name": tenant.full_name,
            "phone_number": tenant.phone_number,
            "email": tenant.email,
            "balance": tenant.balance,
            "assigned_room_id": tenant.assigned_room_id,
            "room_number": None
        }
        
        # Get room number if assigned
        if tenant.assigned_room_id:
            room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
            if room:
                tenant_data["room_number"] = room.room_number
        
        result.append(tenant_data)
    
    return result


def update_tenant(db: Session, tenant_id: int, **kwargs):
    """Update tenant information - takes any keyword arguments"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    # Update only provided fields
    for key, value in kwargs.items():
        if hasattr(db_tenant, key) and value is not None:
            setattr(db_tenant, key, value)
    
    db.commit()
    db.refresh(db_tenant)
    
    return db_tenant


def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
    """Assign tenant to a room"""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")
    
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        raise ValueError("Room not found")
    
    if room.is_occupied:
        raise ValueError("Room is already occupied")
    
    # Assign tenant
    tenant.assigned_room_id = room_id
    tenant.balance = room.rent_amount  # Set initial balance to first month rent
    
    # Mark room as occupied
    room.is_occupied = True
    
    db.commit()
    db.refresh(tenant)
    
    return tenant


def get_archived_tenants(db: Session, landlord_id: int):
    """Get all archived tenants for a landlord"""
    archived = db.query(ArchivedTenant).filter(
        ArchivedTenant.landlord_id == landlord_id
    ).order_by(ArchivedTenant.archived_at.desc()).all()
    
    return archived










# from sqlalchemy.orm import Session
# from ..models import Tenant, ArchivedTenant, Room
# from ..schemas import TenantCreate
# from sqlalchemy.sql import func

# def create_tenant(db: Session, tenant: TenantCreate):
#     db_tenant = Tenant(**tenant.dict())
#     db.add(db_tenant)
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant

# def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int, rent_amount: float, due_date: int):
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     db_room = db.query(Room).filter(Room.room_id == room_id).first()
#     if not db_tenant or not db_room:
#         return None
#     db_tenant.assigned_room_id = room_id
#     db_tenant.balance = rent_amount
#     db_room.due_date = due_date
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant

# def deactivate_tenant(db: Session, tenant_id: int):
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not db_tenant:
#         return None
#     db_tenant.is_active = False
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant

# def vacate_and_archive_tenant(db: Session, tenant_id: int):
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not db_tenant:
#         return None
#     # Archive
#     db_archived = ArchivedTenant(
#         original_tenant_id=db_tenant.tenant_id,
#         full_name=db_tenant.full_name,
#         phone_number=db_tenant.phone_number,
#         email=db_tenant.email,
#         faculty=db_tenant.faculty,
#         year_of_study=db_tenant.year_of_study,
#         guardian_phone_number=db_tenant.guardian_phone_number,
#         guardian_name=db_tenant.guardian_name,
#         guardian_location=db_tenant.guardian_location,
#         photo=db_tenant.photo,
#         id_card_number=db_tenant.id_card_number,
#         balance=db_tenant.balance,
#         archived_at=func.now()
#     )
#     db.add(db_archived)
#     # Vacate
#     db_tenant.assigned_room_id = None
#     db_tenant.is_active = False
#     db.commit()
#     db.refresh(db_tenant)
#     db.refresh(db_archived)
#     return db_archived