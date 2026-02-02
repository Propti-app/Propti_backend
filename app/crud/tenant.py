# app/crud/tenant.py - COMPLETE PRODUCTION-READY VERSION
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Tenant, Room, Property, ArchivedTenant
from app.schemas import TenantCreate
from datetime import datetime

def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
    """Create a new tenant linked to landlord"""
    db_tenant = Tenant(
        landlord_id=landlord_id,  # ← Security: Link to landlord
        full_name=tenant.full_name,
        phone_number=tenant.phone_number,
        email=tenant.email,
        id_card_number=tenant.id_card_number,
        faculty=tenant.faculty,
        year_of_study=tenant.year_of_study,
        guardian_name=tenant.guardian_name,
        guardian_phone_number=tenant.guardian_phone_number,
        guardian_location=tenant.guardian_location,
        is_active=True,
        balance=0.0
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenant(db: Session, tenant_id: int, landlord_id: int):
    """Get tenant - ONLY if they belong to this landlord"""
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord_id  # ← Security filter
    ).first()
    
    if not tenant:
        return None
    
    # Get room info if assigned
    room_number = None
    room_rent = None
    property_name = None
    
    if tenant.assigned_room_id:
        room = db.query(Room).join(Property).filter(
            Room.room_id == tenant.assigned_room_id
        ).first()
        
        if room:
            room_number = room.room_number
            room_rent = room.rent_amount
            property_name = room.property.name if room.property else None
    
    return {
        "tenant_id": tenant.tenant_id,
        "landlord_id": tenant.landlord_id,
        "full_name": tenant.full_name,
        "phone_number": tenant.phone_number,
        "email": tenant.email,
        "id_card_number": tenant.id_card_number,
        "faculty": tenant.faculty,
        "year_of_study": tenant.year_of_study,
        "guardian_name": tenant.guardian_name,
        "guardian_phone": tenant.guardian_phone_number,
        "guardian_location": tenant.guardian_location,
        "assigned_room_id": tenant.assigned_room_id,
        "balance": tenant.balance,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at,
        "room_number": room_number,
        "property_name": property_name,
        "room_rent": room_rent
    }


def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    """Get all active tenants for THIS landlord"""
    tenants = db.query(Tenant).filter(
        Tenant.landlord_id == landlord_id,  # ← Security filter
        Tenant.is_active == True
    ).offset(skip).limit(limit).all()
    
    result = []
    for tenant in tenants:
        room_number = None
        if tenant.assigned_room_id:
            room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
            if room:
                room_number = room.room_number
        
        tenant_dict = {
            "tenant_id": tenant.tenant_id,
            "full_name": tenant.full_name,
            "phone_number": tenant.phone_number,
            "email": tenant.email,
            "faculty": tenant.faculty,
            "year_of_study": tenant.year_of_study,
            "guardian_phone_number": tenant.guardian_phone_number,
            "guardian_name": tenant.guardian_name,
            "guardian_location": tenant.guardian_location,
            "photo": tenant.photo,
            "id_card_number": tenant.id_card_number,
            "assigned_room_id": tenant.assigned_room_id,
            "balance": tenant.balance,
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at,
            "is_active": tenant.is_active,
            "room_number": room_number
        }
        result.append(tenant_dict)
    
    return result


def update_tenant(db: Session, tenant_id: int, **kwargs):
    """Update tenant information"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    # Map guardian_phone to guardian_phone_number
    if 'guardian_phone' in kwargs:
        kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
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
    
    # Check if room is occupied
    if room.is_occupied:
        raise ValueError("Room is already occupied")
    
    # If tenant was previously in another room, vacate it
    if tenant.assigned_room_id:
        old_room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
        if old_room:
            old_room.is_occupied = False
    
    # Assign to new room
    tenant.assigned_room_id = room_id
    tenant.balance = room.rent_amount
    room.is_occupied = True
    
    db.commit()
    db.refresh(tenant)
    
    return tenant


def vacate_and_archive_tenant(db: Session, tenant_id: int):
    """Vacate tenant and archive their data"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    # Get room info before vacating
    room_number = None
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room_number = room.room_number
            # Mark room as vacant
            room.is_occupied = False
    
    # Create archived record
    db_archived = ArchivedTenant(
        original_tenant_id=db_tenant.tenant_id,
        landlord_id=db_tenant.landlord_id,
        full_name=db_tenant.full_name,
        phone_number=db_tenant.phone_number,
        email=db_tenant.email,
        room_number=room_number,
        final_balance=db_tenant.balance,
        archived_at=func.now()
    )
    
    db.add(db_archived)
    
    # Deactivate tenant
    db_tenant.assigned_room_id = None
    db_tenant.is_active = False
    
    db.commit()
    db.refresh(db_archived)
    
    return db_archived


def deactivate_tenant(db: Session, tenant_id: int):
    """Deactivate a tenant without archiving"""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")
    
    # Vacate room if assigned
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room.is_occupied = False
        db_tenant.assigned_room_id = None
    
    db_tenant.is_active = False
    
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_archived_tenants(db: Session, landlord_id: int):
    """Get all archived tenants for this landlord"""
    archived = db.query(ArchivedTenant).filter(
        ArchivedTenant.landlord_id == landlord_id  # ← Security filter
    ).order_by(ArchivedTenant.archived_at.desc()).all()
    
    return archived








# # app/crud/tenant.py - FINAL WORKING VERSION MATCHING YOUR ACTUAL MODELS
# from sqlalchemy.orm import Session
# from sqlalchemy import func
# from app.models import Tenant, Room, Property, ArchivedTenant
# from app.schemas import TenantCreate
# from datetime import datetime

# def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
#     """Create a new tenant"""
#     db_tenant = Tenant(
#         full_name=tenant.full_name,
#         phone_number=tenant.phone_number,
#         email=tenant.email,
#         id_card_number=tenant.id_card_number,
#         faculty=tenant.faculty,
#         year_of_study=tenant.year_of_study,
#         guardian_name=tenant.guardian_name,
#         guardian_phone_number=tenant.guardian_phone_number,
#         guardian_location=tenant.guardian_location,
#         is_active=True,
#         balance=0.0
#     )
#     db.add(db_tenant)
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant


# def vacate_and_archive_tenant(db: Session, tenant_id: int):
#     """Vacate tenant and archive their data"""
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not db_tenant:
#         raise ValueError("Tenant not found")
    
#     room_number = None
#     if db_tenant.assigned_room_id:
#         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
#         if room:
#             room_number = room.room_number
    
#     # Create archived record - ONLY with fields that exist in ArchivedTenant
#     db_archived = ArchivedTenant(
#         original_tenant_id=db_tenant.tenant_id,
#         full_name=db_tenant.full_name,
#         phone_number=db_tenant.phone_number,
#         email=db_tenant.email,
#         balance=db_tenant.balance,
#         archived_at=func.now()
#     )
    
#     db.add(db_archived)
    
#     # Clear room assignment
#     db_tenant.assigned_room_id = None
#     db_tenant.is_active = False
    
#     db.commit()
#     db.refresh(db_archived)
    
#     return db_archived


# def deactivate_tenant(db: Session, tenant_id: int):
#     """Deactivate a tenant (soft delete)"""
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not db_tenant:
#         raise ValueError("Tenant not found")
    
#     db_tenant.is_active = False
    
#     # Clear room assignment if exists
#     if db_tenant.assigned_room_id:
#         db_tenant.assigned_room_id = None
    
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant


# def get_tenant(db: Session, tenant_id: int, landlord_id: int):
#     """Get tenant with room information - SECURE"""
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not tenant:
#         return None
    
#     # Security check: verify tenant belongs to landlord's property
#     if tenant.assigned_room_id:
#         room = db.query(Room).join(Property).filter(
#             Room.room_id == tenant.assigned_room_id,
#             Property.landlord_id == landlord_id
#         ).first()
#         if not room:
#             # Tenant has a room but it doesn't belong to this landlord
#             return None
#     else:
#         # Unassigned tenant - allow access (temporary until landlord_id added to Tenant)
#         pass
    
#     # Get room info if assigned
#     room_number = None
#     room_rent = None
#     property_name = None
    
#     if tenant.assigned_room_id:
#         room = db.query(Room).join(Property).filter(
#             Room.room_id == tenant.assigned_room_id
#         ).first()
        
#         if room:
#             room_number = room.room_number
#             room_rent = room.rent_amount
#             property_name = room.property.name if room.property else None
    
#     return {
#         "tenant_id": tenant.tenant_id,
#         "landlord_id": landlord_id,  # Pass through for response
#         "full_name": tenant.full_name,
#         "phone_number": tenant.phone_number,
#         "email": tenant.email,
#         "id_card_number": tenant.id_card_number,
#         "faculty": tenant.faculty,
#         "year_of_study": tenant.year_of_study,
#         "guardian_name": tenant.guardian_name,
#         "guardian_phone": tenant.guardian_phone_number,
#         "guardian_location": tenant.guardian_location,
#         "assigned_room_id": tenant.assigned_room_id,
#         "balance": tenant.balance,
#         "is_active": tenant.is_active,
#         "created_at": tenant.created_at,
#         "room_number": room_number,
#         "property_name": property_name,
#         "room_rent": room_rent
#     }


# def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
#     """Get all active tenants for THIS LANDLORD"""
#     # Get tenants assigned to landlord's rooms
#     assigned_tenants = db.query(Tenant).join(
#         Room, Tenant.assigned_room_id == Room.room_id
#     ).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Property.landlord_id == landlord_id,
#         Tenant.is_active == True
#     ).all()
    
#     # Also get unassigned active tenants (temporary until landlord_id added)
#     unassigned_tenants = db.query(Tenant).filter(
#         Tenant.assigned_room_id == None,
#         Tenant.is_active == True
#     ).all()
    
#     # Combine both lists
#     all_tenants = assigned_tenants + unassigned_tenants
    
#     # Apply skip/limit
#     tenants = all_tenants[skip:skip + limit]
    
#     result = []
#     for tenant in tenants:
#         room_number = None
#         if tenant.assigned_room_id:
#             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
#             if room:
#                 room_number = room.room_number
        
#         tenant_dict = {
#             "tenant_id": tenant.tenant_id,
#             "full_name": tenant.full_name,
#             "phone_number": tenant.phone_number,
#             "email": tenant.email,
#             "faculty": tenant.faculty,
#             "year_of_study": tenant.year_of_study,
#             "guardian_phone_number": tenant.guardian_phone_number,
#             "guardian_name": tenant.guardian_name,
#             "guardian_location": tenant.guardian_location,
#             "photo": tenant.photo,
#             "id_card_number": tenant.id_card_number,
#             "assigned_room_id": tenant.assigned_room_id,
#             "balance": tenant.balance,
#             "created_at": tenant.created_at,
#             "updated_at": tenant.updated_at,
#             "is_active": tenant.is_active,
#             "room_number": room_number
#         }
#         result.append(tenant_dict)
    
#     return result


# def update_tenant(db: Session, tenant_id: int, **kwargs):
#     """Update tenant information"""
#     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not db_tenant:
#         raise ValueError("Tenant not found")
    
#     # Handle guardian_phone mapping
#     if 'guardian_phone' in kwargs:
#         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
#     # Update fields
#     for key, value in kwargs.items():
#         if hasattr(db_tenant, key) and value is not None:
#             setattr(db_tenant, key, value)
    
#     db.commit()
#     db.refresh(db_tenant)
    
#     return db_tenant


# def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
#     """
#     Assign tenant to a room
#     NO is_occupied field - we check by querying for existing assignments
#     """
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
#     if not tenant:
#         raise ValueError("Tenant not found")
    
#     room = db.query(Room).filter(Room.room_id == room_id).first()
#     if not room:
#         raise ValueError("Room not found")
    
#     # Check if room is already occupied by another active tenant
#     existing_tenant = db.query(Tenant).filter(
#         Tenant.assigned_room_id == room_id,
#         Tenant.is_active == True,
#         Tenant.tenant_id != tenant_id  # Allow reassigning same tenant
#     ).first()
    
#     if existing_tenant:
#         raise ValueError("Room is already occupied")
    
#     # Assign tenant to room
#     tenant.assigned_room_id = room_id
#     tenant.balance = room.rent_amount
    
#     db.commit()
#     db.refresh(tenant)
    
#     return tenant


# def get_archived_tenants(db: Session, landlord_id: int):
#     """Get all archived tenants"""
#     # Note: ArchivedTenant doesn't have landlord_id, so we return all
#     # This is a limitation of current model
#     archived = db.query(ArchivedTenant).order_by(
#         ArchivedTenant.archived_at.desc()
#     ).all()
    
#     return archived












# # # app/crud/tenant.py - FINAL SECURE VERSION WITH LANDLORD_ID
# # from sqlalchemy.orm import Session
# # from sqlalchemy import func
# # from app.models import Tenant, Room, Property, ArchivedTenant
# # from app.schemas import TenantCreate
# # from datetime import datetime

# # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# #     """
# #     Create a new tenant LINKED TO THIS LANDLORD
# #     This is the key security fix - tenant belongs to landlord from creation
# #     """
# #     db_tenant = Tenant(
# #         landlord_id=landlord_id,  # ← THE CRITICAL FIX
# #         full_name=tenant.full_name,
# #         phone_number=tenant.phone_number,
# #         email=tenant.email,
# #         id_card_number=tenant.id_card_number,
# #         faculty=tenant.faculty,
# #         year_of_study=tenant.year_of_study,
# #         guardian_name=tenant.guardian_name,
# #         guardian_phone_number=tenant.guardian_phone_number,
# #         guardian_location=tenant.guardian_location,
# #         is_active=True,
# #         balance=0.0
# #     )
# #     db.add(db_tenant)
# #     db.commit()
# #     db.refresh(db_tenant)
# #     return db_tenant


# # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# #     """Vacate tenant and archive their data"""
# #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# #     if not db_tenant:
# #         raise ValueError("Tenant not found")
    
# #     room_info = None
# #     if db_tenant.assigned_room_id:
# #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# #         if room:
# #             room_info = room.room_number
    
# #     # ArchivedTenant
# #     db_archived = ArchivedTenant(
# #         original_tenant_id=db_tenant.tenant_id,
# #         full_name=db_tenant.full_name,
# #         phone_number=db_tenant.phone_number,
# #         email=db_tenant.email,
# #         balance=db_tenant.balance,
# #         archived_at=func.now()
# #     )
    
# #     db.add(db_archived)
    
# #     if db_tenant.assigned_room_id:
# #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# #         if room:
# #             room.is_occupied = False
    
# #     db_tenant.assigned_room_id = None
# #     db_tenant.is_active = False
    
# #     db.commit()
# #     db.refresh(db_archived)
    
# #     return db_archived


# # def deactivate_tenant(db: Session, tenant_id: int):
# #     """Deactivate a tenant"""
# #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# #     if not db_tenant:
# #         raise ValueError("Tenant not found")
    
# #     db_tenant.is_active = False
    
# #     if db_tenant.assigned_room_id:
# #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# #         if room:
# #             room.is_occupied = False
# #         db_tenant.assigned_room_id = None
    
# #     db.commit()
# #     db.refresh(db_tenant)
# #     return db_tenant


# # def get_tenant(db: Session, tenant_id: int, landlord_id: int):
# #     """Get tenant - ONLY if they belong to this landlord"""
# #     tenant = db.query(Tenant).filter(
# #         Tenant.tenant_id == tenant_id,
# #         Tenant.landlord_id == landlord_id  # ← SECURE: Filter by landlord
# #     ).first()
    
# #     if not tenant:
# #         return None
    
# #     # Get room info if assigned
# #     room = None
# #     room_number = None
# #     room_rent = None
# #     property_name = None
    
# #     if tenant.assigned_room_id:
# #         room = db.query(Room).join(Property).filter(
# #             Room.room_id == tenant.assigned_room_id
# #         ).first()
        
# #         if room:
# #             room_number = room.room_number
# #             room_rent = room.rent_amount
# #             property_name = room.property.name if room.property else None
    
# #     return {
# #         "tenant_id": tenant.tenant_id,
# #         "landlord_id": tenant.landlord_id,
# #         "full_name": tenant.full_name,
# #         "phone_number": tenant.phone_number,
# #         "email": tenant.email,
# #         "id_card_number": tenant.id_card_number,
# #         "faculty": tenant.faculty,
# #         "year_of_study": tenant.year_of_study,
# #         "guardian_name": tenant.guardian_name,
# #         "guardian_phone": tenant.guardian_phone_number,
# #         "guardian_location": tenant.guardian_location,
# #         "assigned_room_id": tenant.assigned_room_id,
# #         "balance": tenant.balance,
# #         "is_active": tenant.is_active,
# #         "created_at": tenant.created_at,
# #         "room_number": room_number,
# #         "property_name": property_name,
# #         "room_rent": room_rent
# #     }


# # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# #     """Get all active tenants - ONLY for this landlord"""
# #     tenants = db.query(Tenant).filter(
# #         Tenant.landlord_id == landlord_id,  # ← SECURE: Only YOUR tenants
# #         Tenant.is_active == True
# #     ).offset(skip).limit(limit).all()
    
# #     result = []
# #     for tenant in tenants:
# #         room_number = None
# #         if tenant.assigned_room_id:
# #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# #             if room:
# #                 room_number = room.room_number
        
# #         tenant_dict = {
# #             "tenant_id": tenant.tenant_id,
# #             "full_name": tenant.full_name,
# #             "phone_number": tenant.phone_number,
# #             "email": tenant.email,
# #             "faculty": tenant.faculty,
# #             "year_of_study": tenant.year_of_study,
# #             "guardian_phone_number": tenant.guardian_phone_number,
# #             "guardian_name": tenant.guardian_name,
# #             "guardian_location": tenant.guardian_location,
# #             "photo": tenant.photo,
# #             "id_card_number": tenant.id_card_number,
# #             "assigned_room_id": tenant.assigned_room_id,
# #             "balance": tenant.balance,
# #             "created_at": tenant.created_at,
# #             "updated_at": tenant.updated_at,
# #             "is_active": tenant.is_active,
# #             "room_number": room_number
# #         }
# #         result.append(tenant_dict)
    
# #     return result


# # def update_tenant(db: Session, tenant_id: int, **kwargs):
# #     """Update tenant information"""
# #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# #     if not db_tenant:
# #         raise ValueError("Tenant not found")
    
# #     if 'guardian_phone' in kwargs:
# #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# #     for key, value in kwargs.items():
# #         if hasattr(db_tenant, key) and value is not None:
# #             setattr(db_tenant, key, value)
    
# #     db.commit()
# #     db.refresh(db_tenant)
    
# #     return db_tenant


# # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# #     """Assign tenant to a room"""
# #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# #     if not tenant:
# #         raise ValueError("Tenant not found")
    
# #     room = db.query(Room).filter(Room.room_id == room_id).first()
# #     if not room:
# #         raise ValueError("Room not found")
    
# #     if room.is_occupied:
# #         raise ValueError("Room is already occupied")
    
# #     tenant.assigned_room_id = room_id
# #     tenant.balance = room.rent_amount
# #     room.is_occupied = True
    
# #     db.commit()
# #     db.refresh(tenant)
    
# #     return tenant


# # def get_archived_tenants(db: Session, landlord_id: int):
# #     """Get all archived tenants"""
# #     # Note: ArchivedTenant doesn't have landlord_id field
# #     # This is a limitation of the current model
# #     archived = db.query(ArchivedTenant).order_by(ArchivedTenant.archived_at.desc()).all()
    
# #     return archived




# # # # app/crud/tenant.py - FIXED VERSION - ALLOWS UNASSIGNED TENANTS
# # # from sqlalchemy.orm import Session
# # # from sqlalchemy import func
# # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # from app.schemas import TenantCreate
# # # from datetime import datetime

# # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # #     """Create a new tenant"""
# # #     db_tenant = Tenant(
# # #         full_name=tenant.full_name,
# # #         phone_number=tenant.phone_number,
# # #         email=tenant.email,
# # #         id_card_number=tenant.id_card_number,
# # #         faculty=tenant.faculty,
# # #         year_of_study=tenant.year_of_study,
# # #         guardian_name=tenant.guardian_name,
# # #         guardian_phone_number=tenant.guardian_phone_number,
# # #         guardian_location=tenant.guardian_location,
# # #         is_active=True,
# # #         balance=0.0
# # #     )
# # #     db.add(db_tenant)
# # #     db.commit()
# # #     db.refresh(db_tenant)
# # #     return db_tenant


# # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # #     """Vacate tenant and archive their data"""
# # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # #     if not db_tenant:
# # #         raise ValueError("Tenant not found")
    
# # #     room_info = None
# # #     if db_tenant.assigned_room_id:
# # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # #         if room:
# # #             room_info = room.room_number
    
# # #     # ArchivedTenant - only fields that exist in the model
# # #     db_archived = ArchivedTenant(
# # #         original_tenant_id=db_tenant.tenant_id,
# # #         full_name=db_tenant.full_name,
# # #         phone_number=db_tenant.phone_number,
# # #         email=db_tenant.email,
# # #         room_number=room_info,
# # #         final_balance=db_tenant.balance,
# # #         archived_at=func.now()
# # #     )
    
# # #     db.add(db_archived)
    
# # #     if db_tenant.assigned_room_id:
# # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # #         if room:
# # #             room.is_occupied = False
    
# # #     db_tenant.assigned_room_id = None
# # #     db_tenant.is_active = False
    
# # #     db.commit()
# # #     db.refresh(db_archived)
    
# # #     return db_archived


# # # def deactivate_tenant(db: Session, tenant_id: int):
# # #     """Deactivate a tenant"""
# # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # #     if not db_tenant:
# # #         raise ValueError("Tenant not found")
    
# # #     db_tenant.is_active = False
    
# # #     if db_tenant.assigned_room_id:
# # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # #         if room:
# # #             room.is_occupied = False
# # #         db_tenant.assigned_room_id = None
    
# # #     db.commit()
# # #     db.refresh(db_tenant)
# # #     return db_tenant


# # # def get_tenant(db: Session, tenant_id: int, landlord_id: int):
# # #     """Get tenant with room information - ALLOWS UNASSIGNED TENANTS"""
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # #     if not tenant:
# # #         return None
    
# # #     # Get room info if tenant is assigned
# # #     room = None
# # #     if tenant.assigned_room_id:
# # #         room = db.query(Room).join(Property).filter(
# # #             Room.room_id == tenant.assigned_room_id,
# # #             Property.landlord_id == landlord_id
# # #         ).first()
# # #         if not room:
# # #             # Tenant has a room but it doesn't belong to this landlord - DENY ACCESS
# # #             return None
    
# # #     # If no room assigned, allow access (newly created tenant)
# # #     # Build response
# # #     landlord_id_val = landlord_id
# # #     room_number = room.room_number if room else None
# # #     room_rent = room.rent_amount if room else None
# # #     property_name = room.property.name if room and room.property else None
    
# # #     return {
# # #         "tenant_id": tenant.tenant_id,
# # #         "landlord_id": landlord_id_val,
# # #         "full_name": tenant.full_name,
# # #         "phone_number": tenant.phone_number,
# # #         "email": tenant.email,
# # #         "id_card_number": tenant.id_card_number,
# # #         "faculty": tenant.faculty,
# # #         "year_of_study": tenant.year_of_study,
# # #         "guardian_name": tenant.guardian_name,
# # #         "guardian_phone": tenant.guardian_phone_number,
# # #         "guardian_location": tenant.guardian_location,
# # #         "assigned_room_id": tenant.assigned_room_id,
# # #         "balance": tenant.balance,
# # #         "is_active": tenant.is_active,
# # #         "created_at": tenant.created_at,
# # #         "room_number": room_number,
# # #         "property_name": property_name,
# # #         "room_rent": room_rent
# # #     }


# # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # #     """Get all active tenants for THIS LANDLORD - INCLUDES UNASSIGNED TENANTS"""
# # #     # Get tenants that are either:
# # #     # 1. Assigned to this landlord's rooms
# # #     # 2. Not assigned to any room (newly created)
    
# # #     # First, get tenants assigned to landlord's rooms
# # #     assigned_tenants = db.query(Tenant).join(
# # #         Room, Tenant.assigned_room_id == Room.room_id
# # #     ).join(
# # #         Property, Room.property_id == Property.property_id
# # #     ).filter(
# # #         Property.landlord_id == landlord_id,
# # #         Tenant.is_active == True
# # #     ).all()
    
# # #     # Then, get unassigned active tenants
# # #     unassigned_tenants = db.query(Tenant).filter(
# # #         Tenant.assigned_room_id == None,
# # #         Tenant.is_active == True
# # #     ).all()
    
# # #     # Combine both lists
# # #     all_tenants = assigned_tenants + unassigned_tenants
    
# # #     # Apply skip/limit
# # #     tenants = all_tenants[skip:skip + limit]
    
# # #     result = []
# # #     for tenant in tenants:
# # #         room_number = None
# # #         if tenant.assigned_room_id:
# # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # #             if room:
# # #                 room_number = room.room_number
        
# # #         tenant_dict = {
# # #             "tenant_id": tenant.tenant_id,
# # #             "full_name": tenant.full_name,
# # #             "phone_number": tenant.phone_number,
# # #             "email": tenant.email,
# # #             "faculty": tenant.faculty,
# # #             "year_of_study": tenant.year_of_study,
# # #             "guardian_phone_number": tenant.guardian_phone_number,
# # #             "guardian_name": tenant.guardian_name,
# # #             "guardian_location": tenant.guardian_location,
# # #             "photo": tenant.photo,
# # #             "id_card_number": tenant.id_card_number,
# # #             "assigned_room_id": tenant.assigned_room_id,
# # #             "balance": tenant.balance,
# # #             "created_at": tenant.created_at,
# # #             "updated_at": tenant.updated_at,
# # #             "is_active": tenant.is_active,
# # #             "room_number": room_number
# # #         }
# # #         result.append(tenant_dict)
    
# # #     return result


# # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # #     """Update tenant information"""
# # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # #     if not db_tenant:
# # #         raise ValueError("Tenant not found")
    
# # #     if 'guardian_phone' in kwargs:
# # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # #     for key, value in kwargs.items():
# # #         if hasattr(db_tenant, key) and value is not None:
# # #             setattr(db_tenant, key, value)
    
# # #     db.commit()
# # #     db.refresh(db_tenant)
    
# # #     return db_tenant


# # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # #     """Assign tenant to a room"""
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # #     if not tenant:
# # #         raise ValueError("Tenant not found")
    
# # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # #     if not room:
# # #         raise ValueError("Room not found")
    
# # #     if room.is_occupied:
# # #         raise ValueError("Room is already occupied")
    
# # #     tenant.assigned_room_id = room_id
# # #     tenant.balance = room.rent_amount
# # #     room.is_occupied = True
    
# # #     db.commit()
# # #     db.refresh(tenant)
    
# # #     return tenant


# # # def get_archived_tenants(db: Session, landlord_id: int):
# # #     """Get all archived tenants - NO LANDLORD FILTER (model doesn't have it)"""
# # #     # Note: ArchivedTenant doesn't have landlord_id, so we can't filter
# # #     # This is a data model issue that should be fixed in the future
# # #     archived = db.query(ArchivedTenant).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # #     return archived




# # # # # app/crud/tenant.py - SECURE WITH PROPER LANDLORD FILTERING
# # # # from sqlalchemy.orm import Session
# # # # from sqlalchemy import func
# # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # from app.schemas import TenantCreate
# # # # from datetime import datetime

# # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # #     """Create a new tenant"""
# # # #     db_tenant = Tenant(
# # # #         full_name=tenant.full_name,
# # # #         phone_number=tenant.phone_number,
# # # #         email=tenant.email,
# # # #         id_card_number=tenant.id_card_number,
# # # #         faculty=tenant.faculty,
# # # #         year_of_study=tenant.year_of_study,
# # # #         guardian_name=tenant.guardian_name,
# # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # #         guardian_location=tenant.guardian_location,
# # # #         is_active=True,
# # # #         balance=0.0
# # # #     )
# # # #     db.add(db_tenant)
# # # #     db.commit()
# # # #     db.refresh(db_tenant)
# # # #     return db_tenant


# # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # #     """Vacate tenant and archive their data"""
# # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # #     if not db_tenant:
# # # #         raise ValueError("Tenant not found")
    
# # # #     room_info = None
# # # #     if db_tenant.assigned_room_id:
# # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # #         if room:
# # # #             room_info = room.room_number
    
# # # #     # ArchivedTenant - only fields that exist in the model
# # # #     db_archived = ArchivedTenant(
# # # #         original_tenant_id=db_tenant.tenant_id,
# # # #         full_name=db_tenant.full_name,
# # # #         phone_number=db_tenant.phone_number,
# # # #         email=db_tenant.email,
# # # #         room_number=room_info,
# # # #         final_balance=db_tenant.balance,
# # # #         archived_at=func.now()
# # # #     )
    
# # # #     db.add(db_archived)
    
# # # #     if db_tenant.assigned_room_id:
# # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # #         if room:
# # # #             room.is_occupied = False
    
# # # #     db_tenant.assigned_room_id = None
# # # #     db_tenant.is_active = False
    
# # # #     db.commit()
# # # #     db.refresh(db_archived)
    
# # # #     return db_archived


# # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # #     """Deactivate a tenant"""
# # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # #     if not db_tenant:
# # # #         raise ValueError("Tenant not found")
    
# # # #     db_tenant.is_active = False
    
# # # #     if db_tenant.assigned_room_id:
# # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # #         if room:
# # # #             room.is_occupied = False
# # # #         db_tenant.assigned_room_id = None
    
# # # #     db.commit()
# # # #     db.refresh(db_tenant)
# # # #     return db_tenant


# # # # def get_tenant(db: Session, tenant_id: int, landlord_id: int):
# # # #     """Get tenant with room information - SECURE WITH LANDLORD CHECK"""
# # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # #     if not tenant:
# # # #         return None
    
# # # #     # SECURITY: Verify tenant belongs to landlord
# # # #     if tenant.assigned_room_id:
# # # #         room = db.query(Room).join(Property).filter(
# # # #             Room.room_id == tenant.assigned_room_id,
# # # #             Property.landlord_id == landlord_id
# # # #         ).first()
# # # #         if not room:
# # # #             # Tenant doesn't belong to this landlord
# # # #             return None
# # # #     else:
# # # #         # Unassigned tenant - can't verify ownership, deny access
# # # #         return None
    
# # # #     landlord_id_val = landlord_id
# # # #     room_number = room.room_number if room else None
# # # #     room_rent = room.rent_amount if room else None
# # # #     property_name = room.property.name if room and room.property else None
    
# # # #     return {
# # # #         "tenant_id": tenant.tenant_id,
# # # #         "landlord_id": landlord_id_val,
# # # #         "full_name": tenant.full_name,
# # # #         "phone_number": tenant.phone_number,
# # # #         "email": tenant.email,
# # # #         "id_card_number": tenant.id_card_number,
# # # #         "faculty": tenant.faculty,
# # # #         "year_of_study": tenant.year_of_study,
# # # #         "guardian_name": tenant.guardian_name,
# # # #         "guardian_phone": tenant.guardian_phone_number,
# # # #         "guardian_location": tenant.guardian_location,
# # # #         "assigned_room_id": tenant.assigned_room_id,
# # # #         "balance": tenant.balance,
# # # #         "is_active": tenant.is_active,
# # # #         "created_at": tenant.created_at,
# # # #         "room_number": room_number,
# # # #         "property_name": property_name,
# # # #         "room_rent": room_rent
# # # #     }


# # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # #     """Get all active tenants for THIS LANDLORD ONLY - SECURE"""
# # # #     # ONLY get tenants assigned to rooms in landlord's properties
# # # #     tenants = db.query(Tenant).join(
# # # #         Room, Tenant.assigned_room_id == Room.room_id
# # # #     ).join(
# # # #         Property, Room.property_id == Property.property_id
# # # #     ).filter(
# # # #         Property.landlord_id == landlord_id,
# # # #         Tenant.is_active == True
# # # #     ).offset(skip).limit(limit).all()
    
# # # #     result = []
# # # #     for tenant in tenants:
# # # #         room_number = None
# # # #         if tenant.assigned_room_id:
# # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # #             if room:
# # # #                 room_number = room.room_number
        
# # # #         tenant_dict = {
# # # #             "tenant_id": tenant.tenant_id,
# # # #             "full_name": tenant.full_name,
# # # #             "phone_number": tenant.phone_number,
# # # #             "email": tenant.email,
# # # #             "faculty": tenant.faculty,
# # # #             "year_of_study": tenant.year_of_study,
# # # #             "guardian_phone_number": tenant.guardian_phone_number,
# # # #             "guardian_name": tenant.guardian_name,
# # # #             "guardian_location": tenant.guardian_location,
# # # #             "photo": tenant.photo,
# # # #             "id_card_number": tenant.id_card_number,
# # # #             "assigned_room_id": tenant.assigned_room_id,
# # # #             "balance": tenant.balance,
# # # #             "created_at": tenant.created_at,
# # # #             "updated_at": tenant.updated_at,
# # # #             "is_active": tenant.is_active,
# # # #             "room_number": room_number
# # # #         }
# # # #         result.append(tenant_dict)
    
# # # #     return result


# # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # #     """Update tenant information"""
# # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # #     if not db_tenant:
# # # #         raise ValueError("Tenant not found")
    
# # # #     if 'guardian_phone' in kwargs:
# # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # #     for key, value in kwargs.items():
# # # #         if hasattr(db_tenant, key) and value is not None:
# # # #             setattr(db_tenant, key, value)
    
# # # #     db.commit()
# # # #     db.refresh(db_tenant)
    
# # # #     return db_tenant


# # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # #     """Assign tenant to a room"""
# # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # #     if not tenant:
# # # #         raise ValueError("Tenant not found")
    
# # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # #     if not room:
# # # #         raise ValueError("Room not found")
    
# # # #     if room.is_occupied:
# # # #         raise ValueError("Room is already occupied")
    
# # # #     tenant.assigned_room_id = room_id
# # # #     tenant.balance = room.rent_amount
# # # #     room.is_occupied = True
    
# # # #     db.commit()
# # # #     db.refresh(tenant)
    
# # # #     return tenant


# # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # #     """Get all archived tenants - NO LANDLORD FILTER (model doesn't have it)"""
# # # #     # Note: ArchivedTenant doesn't have landlord_id, so we can't filter
# # # #     # This is a data model issue that should be fixed in the future
# # # #     archived = db.query(ArchivedTenant).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # #     return archived

# # # # # # app/crud/tenant.py - FIXED VACATE WITHOUT LANDLORD_ID
# # # # # from sqlalchemy.orm import Session
# # # # # from sqlalchemy import func
# # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # from app.schemas import TenantCreate
# # # # # from datetime import datetime

# # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # #     """Create a new tenant"""
# # # # #     db_tenant = Tenant(
# # # # #         full_name=tenant.full_name,
# # # # #         phone_number=tenant.phone_number,
# # # # #         email=tenant.email,
# # # # #         id_card_number=tenant.id_card_number,
# # # # #         faculty=tenant.faculty,
# # # # #         year_of_study=tenant.year_of_study,
# # # # #         guardian_name=tenant.guardian_name,
# # # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # # #         guardian_location=tenant.guardian_location,
# # # # #         is_active=True,
# # # # #         balance=0.0
# # # # #     )
# # # # #     db.add(db_tenant)
# # # # #     db.commit()
# # # # #     db.refresh(db_tenant)
# # # # #     return db_tenant


# # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # #     """Vacate tenant and archive their data - NO LANDLORD_ID"""
# # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # #     if not db_tenant:
# # # # #         raise ValueError("Tenant not found")
    
# # # # #     room_info = None
# # # # #     if db_tenant.assigned_room_id:
# # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # #         if room:
# # # # #             room_info = room.room_number
    
# # # # #     # ArchivedTenant ONLY has these fields
# # # # #     db_archived = ArchivedTenant(
# # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # #         full_name=db_tenant.full_name,
# # # # #         phone_number=db_tenant.phone_number,
# # # # #         email=db_tenant.email,
# # # # #         room_number=room_info,
# # # # #         final_balance=db_tenant.balance,
# # # # #         archived_at=func.now()
# # # # #     )
    
# # # # #     db.add(db_archived)
    
# # # # #     if db_tenant.assigned_room_id:
# # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # #         if room:
# # # # #             room.is_occupied = False
    
# # # # #     db_tenant.assigned_room_id = None
# # # # #     db_tenant.is_active = False
    
# # # # #     db.commit()
# # # # #     db.refresh(db_archived)
    
# # # # #     return db_archived


# # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # #     """Deactivate a tenant"""
# # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # #     if not db_tenant:
# # # # #         raise ValueError("Tenant not found")
    
# # # # #     db_tenant.is_active = False
    
# # # # #     if db_tenant.assigned_room_id:
# # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # #         if room:
# # # # #             room.is_occupied = False
# # # # #         db_tenant.assigned_room_id = None
    
# # # # #     db.commit()
# # # # #     db.refresh(db_tenant)
# # # # #     return db_tenant


# # # # # def get_tenant(db: Session, tenant_id: int):
# # # # #     """Get tenant with room information"""
# # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # #     if not tenant:
# # # # #         return None
    
# # # # #     landlord_id_val = None
# # # # #     room_number = None
# # # # #     property_name = None
# # # # #     room_rent = None
    
# # # # #     if tenant.assigned_room_id:
# # # # #         room = db.query(Room).join(Property).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # #         if room:
# # # # #             room_number = room.room_number
# # # # #             room_rent = room.rent_amount
# # # # #             property_name = room.property.name
# # # # #             landlord_id_val = room.property.landlord_id
    
# # # # #     return {
# # # # #         "tenant_id": tenant.tenant_id,
# # # # #         "landlord_id": landlord_id_val,
# # # # #         "full_name": tenant.full_name,
# # # # #         "phone_number": tenant.phone_number,
# # # # #         "email": tenant.email,
# # # # #         "id_card_number": tenant.id_card_number,
# # # # #         "faculty": tenant.faculty,
# # # # #         "year_of_study": tenant.year_of_study,
# # # # #         "guardian_name": tenant.guardian_name,
# # # # #         "guardian_phone": tenant.guardian_phone_number,
# # # # #         "guardian_location": tenant.guardian_location,
# # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # #         "balance": tenant.balance,
# # # # #         "is_active": tenant.is_active,
# # # # #         "created_at": tenant.created_at,
# # # # #         "room_number": room_number,
# # # # #         "property_name": property_name,
# # # # #         "room_rent": room_rent
# # # # #     }


# # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # #     """Get all active tenants - RETURNS ALL TENANTS"""
# # # # #     tenants = db.query(Tenant).filter(
# # # # #         Tenant.is_active == True
# # # # #     ).offset(skip).limit(limit).all()
    
# # # # #     result = []
# # # # #     for tenant in tenants:
# # # # #         room_number = None
# # # # #         if tenant.assigned_room_id:
# # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # #             if room:
# # # # #                 room_number = room.room_number
        
# # # # #         tenant_dict = {
# # # # #             "tenant_id": tenant.tenant_id,
# # # # #             "full_name": tenant.full_name,
# # # # #             "phone_number": tenant.phone_number,
# # # # #             "email": tenant.email,
# # # # #             "faculty": tenant.faculty,
# # # # #             "year_of_study": tenant.year_of_study,
# # # # #             "guardian_phone_number": tenant.guardian_phone_number,
# # # # #             "guardian_name": tenant.guardian_name,
# # # # #             "guardian_location": tenant.guardian_location,
# # # # #             "photo": tenant.photo,
# # # # #             "id_card_number": tenant.id_card_number,
# # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # #             "balance": tenant.balance,
# # # # #             "created_at": tenant.created_at,
# # # # #             "updated_at": tenant.updated_at,
# # # # #             "is_active": tenant.is_active,
# # # # #             "room_number": room_number
# # # # #         }
# # # # #         result.append(tenant_dict)
    
# # # # #     return result


# # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # #     """Update tenant information"""
# # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # #     if not db_tenant:
# # # # #         raise ValueError("Tenant not found")
    
# # # # #     if 'guardian_phone' in kwargs:
# # # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # # #     for key, value in kwargs.items():
# # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # #             setattr(db_tenant, key, value)
    
# # # # #     db.commit()
# # # # #     db.refresh(db_tenant)
    
# # # # #     return db_tenant


# # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # #     """Assign tenant to a room"""
# # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # #     if not tenant:
# # # # #         raise ValueError("Tenant not found")
    
# # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # #     if not room:
# # # # #         raise ValueError("Room not found")
    
# # # # #     if room.is_occupied:
# # # # #         raise ValueError("Room is already occupied")
    
# # # # #     tenant.assigned_room_id = room_id
# # # # #     tenant.balance = room.rent_amount
# # # # #     room.is_occupied = True
    
# # # # #     db.commit()
# # # # #     db.refresh(tenant)
    
# # # # #     return tenant


# # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # #     """Get all archived tenants"""
# # # # #     archived = db.query(ArchivedTenant).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # #     return archived




# # # # # # # app/crud/tenant.py - FINAL CLEAN VERSION
# # # # # # from sqlalchemy.orm import Session
# # # # # # from sqlalchemy import func
# # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # from app.schemas import TenantCreate
# # # # # # from datetime import datetime

# # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # #     """Create a new tenant"""
# # # # # #     db_tenant = Tenant(
# # # # # #         full_name=tenant.full_name,
# # # # # #         phone_number=tenant.phone_number,
# # # # # #         email=tenant.email,
# # # # # #         id_card_number=tenant.id_card_number,
# # # # # #         faculty=tenant.faculty,
# # # # # #         year_of_study=tenant.year_of_study,
# # # # # #         guardian_name=tenant.guardian_name,
# # # # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # # # #         guardian_location=tenant.guardian_location,
# # # # # #         is_active=True,
# # # # # #         balance=0.0
# # # # # #     )
# # # # # #     db.add(db_tenant)
# # # # # #     db.commit()
# # # # # #     db.refresh(db_tenant)
# # # # # #     return db_tenant


# # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # #     """Vacate tenant and archive their data"""
# # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # #     if not db_tenant:
# # # # # #         raise ValueError("Tenant not found")
    
# # # # # #     room_info = None
# # # # # #     landlord_id_val = None
# # # # # #     if db_tenant.assigned_room_id:
# # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # #         if room:
# # # # # #             room_info = room.room_number
# # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # #     db_archived = ArchivedTenant(
# # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # #         landlord_id=landlord_id_val,
# # # # # #         full_name=db_tenant.full_name,
# # # # # #         phone_number=db_tenant.phone_number,
# # # # # #         email=db_tenant.email,
# # # # # #         room_number=room_info,
# # # # # #         final_balance=db_tenant.balance,
# # # # # #         archived_at=func.now()
# # # # # #     )
    
# # # # # #     db.add(db_archived)
    
# # # # # #     if db_tenant.assigned_room_id:
# # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # #         if room:
# # # # # #             room.is_occupied = False
    
# # # # # #     db_tenant.assigned_room_id = None
# # # # # #     db_tenant.is_active = False
    
# # # # # #     db.commit()
# # # # # #     db.refresh(db_archived)
    
# # # # # #     return db_archived


# # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # #     """Deactivate a tenant"""
# # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # #     if not db_tenant:
# # # # # #         raise ValueError("Tenant not found")
    
# # # # # #     db_tenant.is_active = False
    
# # # # # #     if db_tenant.assigned_room_id:
# # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # #         if room:
# # # # # #             room.is_occupied = False
# # # # # #         db_tenant.assigned_room_id = None
    
# # # # # #     db.commit()
# # # # # #     db.refresh(db_tenant)
# # # # # #     return db_tenant


# # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # #     """Get tenant with room information"""
# # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # #     if not tenant:
# # # # # #         return None
    
# # # # # #     landlord_id_val = None
# # # # # #     room_number = None
# # # # # #     property_name = None
# # # # # #     room_rent = None
    
# # # # # #     if tenant.assigned_room_id:
# # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # #         if room:
# # # # # #             room_number = room.room_number
# # # # # #             room_rent = room.rent_amount
# # # # # #             property_name = room.property.name  # FIXED: Use 'name' not 'property_name'
# # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # #     return {
# # # # # #         "tenant_id": tenant.tenant_id,
# # # # # #         "landlord_id": landlord_id_val,
# # # # # #         "full_name": tenant.full_name,
# # # # # #         "phone_number": tenant.phone_number,
# # # # # #         "email": tenant.email,
# # # # # #         "id_card_number": tenant.id_card_number,
# # # # # #         "faculty": tenant.faculty,
# # # # # #         "year_of_study": tenant.year_of_study,
# # # # # #         "guardian_name": tenant.guardian_name,
# # # # # #         "guardian_phone": tenant.guardian_phone_number,
# # # # # #         "guardian_location": tenant.guardian_location,
# # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # #         "balance": tenant.balance,
# # # # # #         "is_active": tenant.is_active,
# # # # # #         "created_at": tenant.created_at,
# # # # # #         "room_number": room_number,
# # # # # #         "property_name": property_name,
# # # # # #         "room_rent": room_rent
# # # # # #     }


# # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # #     """Get all active tenants for a landlord - RETURNS ALL TENANTS (WITH AND WITHOUT ROOMS)"""
# # # # # #     # Get ALL tenants, whether they have rooms or not
# # # # # #     tenants = db.query(Tenant).outerjoin(
# # # # # #         Room, Tenant.assigned_room_id == Room.room_id
# # # # # #     ).outerjoin(
# # # # # #         Property, Room.property_id == Property.property_id
# # # # # #     ).filter(
# # # # # #         Tenant.is_active == True
# # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # #     result = []
# # # # # #     for tenant in tenants:
# # # # # #         room_number = None
# # # # # #         if tenant.assigned_room_id:
# # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # #             if room:
# # # # # #                 room_number = room.room_number
        
# # # # # #         tenant_dict = {
# # # # # #             "tenant_id": tenant.tenant_id,
# # # # # #             "full_name": tenant.full_name,
# # # # # #             "phone_number": tenant.phone_number,
# # # # # #             "email": tenant.email,
# # # # # #             "faculty": tenant.faculty,
# # # # # #             "year_of_study": tenant.year_of_study,
# # # # # #             "guardian_phone_number": tenant.guardian_phone_number,
# # # # # #             "guardian_name": tenant.guardian_name,
# # # # # #             "guardian_location": tenant.guardian_location,
# # # # # #             "photo": tenant.photo,
# # # # # #             "id_card_number": tenant.id_card_number,
# # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # #             "balance": tenant.balance,
# # # # # #             "created_at": tenant.created_at,
# # # # # #             "updated_at": tenant.updated_at,
# # # # # #             "is_active": tenant.is_active,
# # # # # #             "room_number": room_number
# # # # # #         }
# # # # # #         result.append(tenant_dict)
    
# # # # # #     return result


# # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # #     """Update tenant information"""
# # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # #     if not db_tenant:
# # # # # #         raise ValueError("Tenant not found")
    
# # # # # #     if 'guardian_phone' in kwargs:
# # # # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # # # #     for key, value in kwargs.items():
# # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # #             setattr(db_tenant, key, value)
    
# # # # # #     db.commit()
# # # # # #     db.refresh(db_tenant)
    
# # # # # #     return db_tenant


# # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # #     """Assign tenant to a room"""
# # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # #     if not tenant:
# # # # # #         raise ValueError("Tenant not found")
    
# # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # #     if not room:
# # # # # #         raise ValueError("Room not found")
    
# # # # # #     if room.is_occupied:
# # # # # #         raise ValueError("Room is already occupied")
    
# # # # # #     tenant.assigned_room_id = room_id
# # # # # #     tenant.balance = room.rent_amount
# # # # # #     room.is_occupied = True
    
# # # # # #     db.commit()
# # # # # #     db.refresh(tenant)
    
# # # # # #     return tenant


# # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # #     """Get all archived tenants for a landlord"""
# # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # #     return archived



# # # # # # # # app/crud/tenant.py - FINAL CLEAN VERSION
# # # # # # # from sqlalchemy.orm import Session
# # # # # # # from sqlalchemy import func
# # # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # # from app.schemas import TenantCreate
# # # # # # # from datetime import datetime

# # # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # # #     """Create a new tenant"""
# # # # # # #     db_tenant = Tenant(
# # # # # # #         full_name=tenant.full_name,
# # # # # # #         phone_number=tenant.phone_number,
# # # # # # #         email=tenant.email,
# # # # # # #         id_card_number=tenant.id_card_number,
# # # # # # #         faculty=tenant.faculty,
# # # # # # #         year_of_study=tenant.year_of_study,
# # # # # # #         guardian_name=tenant.guardian_name,
# # # # # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # # # # #         guardian_location=tenant.guardian_location,
# # # # # # #         is_active=True,
# # # # # # #         balance=0.0
# # # # # # #     )
# # # # # # #     db.add(db_tenant)
# # # # # # #     db.commit()
# # # # # # #     db.refresh(db_tenant)
# # # # # # #     return db_tenant


# # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # #     """Vacate tenant and archive their data"""
# # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # #     if not db_tenant:
# # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # #     room_info = None
# # # # # # #     landlord_id_val = None
# # # # # # #     if db_tenant.assigned_room_id:
# # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # #         if room:
# # # # # # #             room_info = room.room_number
# # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # #     db_archived = ArchivedTenant(
# # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # #         landlord_id=landlord_id_val,
# # # # # # #         full_name=db_tenant.full_name,
# # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # #         email=db_tenant.email,
# # # # # # #         room_number=room_info,
# # # # # # #         final_balance=db_tenant.balance,
# # # # # # #         archived_at=func.now()
# # # # # # #     )
    
# # # # # # #     db.add(db_archived)
    
# # # # # # #     if db_tenant.assigned_room_id:
# # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # #         if room:
# # # # # # #             room.is_occupied = False
    
# # # # # # #     db_tenant.assigned_room_id = None
# # # # # # #     db_tenant.is_active = False
    
# # # # # # #     db.commit()
# # # # # # #     db.refresh(db_archived)
    
# # # # # # #     return db_archived


# # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # #     """Deactivate a tenant"""
# # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # #     if not db_tenant:
# # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # #     db_tenant.is_active = False
    
# # # # # # #     if db_tenant.assigned_room_id:
# # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # #         if room:
# # # # # # #             room.is_occupied = False
# # # # # # #         db_tenant.assigned_room_id = None
    
# # # # # # #     db.commit()
# # # # # # #     db.refresh(db_tenant)
# # # # # # #     return db_tenant


# # # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # # #     """Get tenant with room information"""
# # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # #     if not tenant:
# # # # # # #         return None
    
# # # # # # #     landlord_id_val = None
# # # # # # #     room_number = None
# # # # # # #     property_name = None
# # # # # # #     room_rent = None
    
# # # # # # #     if tenant.assigned_room_id:
# # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # #         if room:
# # # # # # #             room_number = room.room_number
# # # # # # #             room_rent = room.rent_amount
# # # # # # #             property_name = room.property.name  # FIXED: Use 'name' not 'property_name'
# # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # #     return {
# # # # # # #         "tenant_id": tenant.tenant_id,
# # # # # # #         "landlord_id": landlord_id_val,
# # # # # # #         "full_name": tenant.full_name,
# # # # # # #         "phone_number": tenant.phone_number,
# # # # # # #         "email": tenant.email,
# # # # # # #         "id_card_number": tenant.id_card_number,
# # # # # # #         "faculty": tenant.faculty,
# # # # # # #         "year_of_study": tenant.year_of_study,
# # # # # # #         "guardian_name": tenant.guardian_name,
# # # # # # #         "guardian_phone": tenant.guardian_phone_number,
# # # # # # #         "guardian_location": tenant.guardian_location,
# # # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # # #         "balance": tenant.balance,
# # # # # # #         "is_active": tenant.is_active,
# # # # # # #         "created_at": tenant.created_at,
# # # # # # #         "room_number": room_number,
# # # # # # #         "property_name": property_name,
# # # # # # #         "room_rent": room_rent
# # # # # # #     }


# # # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # # #     """Get all active tenants for a landlord - RETURNS ALL TENANTS (WITH AND WITHOUT ROOMS)"""
# # # # # # #     # Get ALL tenants, whether they have rooms or not
# # # # # # #     tenants = db.query(Tenant).outerjoin(
# # # # # # #         Room, Tenant.assigned_room_id == Room.room_id
# # # # # # #     ).outerjoin(
# # # # # # #         Property, Room.property_id == Property.property_id
# # # # # # #     ).filter(
# # # # # # #         Tenant.is_active == True
# # # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # # #     result = []
# # # # # # #     for tenant in tenants:
# # # # # # #         room_number = None
# # # # # # #         if tenant.assigned_room_id:
# # # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # #             if room:
# # # # # # #                 room_number = room.room_number
        
# # # # # # #         tenant_dict = {
# # # # # # #             "tenant_id": tenant.tenant_id,
# # # # # # #             "full_name": tenant.full_name,
# # # # # # #             "phone_number": tenant.phone_number,
# # # # # # #             "email": tenant.email,
# # # # # # #             "faculty": tenant.faculty,
# # # # # # #             "year_of_study": tenant.year_of_study,
# # # # # # #             "guardian_phone_number": tenant.guardian_phone_number,
# # # # # # #             "guardian_name": tenant.guardian_name,
# # # # # # #             "guardian_location": tenant.guardian_location,
# # # # # # #             "photo": tenant.photo,
# # # # # # #             "id_card_number": tenant.id_card_number,
# # # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # # #             "balance": tenant.balance,
# # # # # # #             "created_at": tenant.created_at,
# # # # # # #             "updated_at": tenant.updated_at,
# # # # # # #             "is_active": tenant.is_active,
# # # # # # #             "room_number": room_number
# # # # # # #         }
# # # # # # #         result.append(tenant_dict)
    
# # # # # # #     return result


# # # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # # #     """Update tenant information"""
# # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # #     if not db_tenant:
# # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # #     if 'guardian_phone' in kwargs:
# # # # # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # # # # #     for key, value in kwargs.items():
# # # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # # #             setattr(db_tenant, key, value)
    
# # # # # # #     db.commit()
# # # # # # #     db.refresh(db_tenant)
    
# # # # # # #     return db_tenant


# # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # # #     """Assign tenant to a room"""
# # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # #     if not tenant:
# # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # #     if not room:
# # # # # # #         raise ValueError("Room not found")
    
# # # # # # #     if room.is_occupied:
# # # # # # #         raise ValueError("Room is already occupied")
    
# # # # # # #     tenant.assigned_room_id = room_id
# # # # # # #     tenant.balance = room.rent_amount
# # # # # # #     room.is_occupied = True
    
# # # # # # #     db.commit()
# # # # # # #     db.refresh(tenant)
    
# # # # # # #     return tenant


# # # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # # #     """Get all archived tenants for a landlord"""
# # # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # # #     return archived





# # # # # # # # # app/crud/tenant.py - COMPLETE WITH ALL FIELDS
# # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # from sqlalchemy import func
# # # # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # # # from app.schemas import TenantCreate
# # # # # # # # from datetime import datetime

# # # # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # # # #     """Create a new tenant"""
# # # # # # # #     db_tenant = Tenant(
# # # # # # # #         full_name=tenant.full_name,
# # # # # # # #         phone_number=tenant.phone_number,
# # # # # # # #         email=tenant.email,
# # # # # # # #         id_card_number=tenant.id_card_number,
# # # # # # # #         faculty=tenant.faculty,
# # # # # # # #         year_of_study=tenant.year_of_study,
# # # # # # # #         guardian_name=tenant.guardian_name,
# # # # # # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # # # # # #         guardian_location=tenant.guardian_location,
# # # # # # # #         is_active=True,
# # # # # # # #         balance=0.0
# # # # # # # #     )
# # # # # # # #     db.add(db_tenant)
# # # # # # # #     db.commit()
# # # # # # # #     db.refresh(db_tenant)
# # # # # # # #     return db_tenant


# # # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # # #     """Vacate tenant and archive their data"""
# # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # #     if not db_tenant:
# # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # #     room_info = None
# # # # # # # #     landlord_id_val = None
# # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # #         if room:
# # # # # # # #             room_info = room.room_number
# # # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # # #     db_archived = ArchivedTenant(
# # # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # # #         landlord_id=landlord_id_val,
# # # # # # # #         full_name=db_tenant.full_name,
# # # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # # #         email=db_tenant.email,
# # # # # # # #         room_number=room_info,
# # # # # # # #         final_balance=db_tenant.balance,
# # # # # # # #         archived_at=func.now()
# # # # # # # #     )
    
# # # # # # # #     db.add(db_archived)
    
# # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # #         if room:
# # # # # # # #             room.is_occupied = False
    
# # # # # # # #     db_tenant.assigned_room_id = None
# # # # # # # #     db_tenant.is_active = False
    
# # # # # # # #     db.commit()
# # # # # # # #     db.refresh(db_archived)
    
# # # # # # # #     return db_archived


# # # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # # #     """Deactivate a tenant"""
# # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # #     if not db_tenant:
# # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # #     db_tenant.is_active = False
    
# # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # #         if room:
# # # # # # # #             room.is_occupied = False
# # # # # # # #         db_tenant.assigned_room_id = None
    
# # # # # # # #     db.commit()
# # # # # # # #     db.refresh(db_tenant)
# # # # # # # #     return db_tenant


# # # # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # # # #     """Get tenant with room information"""
# # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # #     if not tenant:
# # # # # # # #         return None
    
# # # # # # # #     landlord_id_val = None
# # # # # # # #     room_number = None
# # # # # # # #     property_name = None
# # # # # # # #     room_rent = None
    
# # # # # # # #     if tenant.assigned_room_id:
# # # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # #         if room:
# # # # # # # #             room_number = room.room_number
# # # # # # # #             room_rent = room.rent_amount
# # # # # # # #             property_name = room.property.property_name
# # # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # # #     return {
# # # # # # # #         "tenant_id": tenant.tenant_id,
# # # # # # # #         "landlord_id": landlord_id_val,
# # # # # # # #         "full_name": tenant.full_name,
# # # # # # # #         "phone_number": tenant.phone_number,
# # # # # # # #         "email": tenant.email,
# # # # # # # #         "id_card_number": tenant.id_card_number,
# # # # # # # #         "faculty": tenant.faculty,
# # # # # # # #         "year_of_study": tenant.year_of_study,
# # # # # # # #         "guardian_name": tenant.guardian_name,
# # # # # # # #         "guardian_phone": tenant.guardian_phone_number,
# # # # # # # #         "guardian_location": tenant.guardian_location,
# # # # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # # # #         "balance": tenant.balance,
# # # # # # # #         "is_active": tenant.is_active,
# # # # # # # #         "created_at": tenant.created_at,
# # # # # # # #         "room_number": room_number,
# # # # # # # #         "property_name": property_name,
# # # # # # # #         "room_rent": room_rent
# # # # # # # #     }


# # # # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # # # #     """Get all active tenants for a landlord - RETURNS FULL TENANT OBJECTS"""
# # # # # # # #     # Get tenants through rooms and properties
# # # # # # # #     tenants = db.query(Tenant).join(
# # # # # # # #         Room, Tenant.assigned_room_id == Room.room_id
# # # # # # # #     ).join(
# # # # # # # #         Property, Room.property_id == Property.property_id
# # # # # # # #     ).filter(
# # # # # # # #         Property.landlord_id == landlord_id,
# # # # # # # #         Tenant.is_active == True
# # # # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # # # #     # Return the actual tenant objects with room_number added
# # # # # # # #     result = []
# # # # # # # #     for tenant in tenants:
# # # # # # # #         # Get room number
# # # # # # # #         room_number = None
# # # # # # # #         if tenant.assigned_room_id:
# # # # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # #             if room:
# # # # # # # #                 room_number = room.room_number
        
# # # # # # # #         # Create a dict-like object that matches TenantResponse schema
# # # # # # # #         tenant_dict = {
# # # # # # # #             "tenant_id": tenant.tenant_id,
# # # # # # # #             "full_name": tenant.full_name,
# # # # # # # #             "phone_number": tenant.phone_number,
# # # # # # # #             "email": tenant.email,
# # # # # # # #             "faculty": tenant.faculty,
# # # # # # # #             "year_of_study": tenant.year_of_study,
# # # # # # # #             "guardian_phone_number": tenant.guardian_phone_number,
# # # # # # # #             "guardian_name": tenant.guardian_name,
# # # # # # # #             "guardian_location": tenant.guardian_location,
# # # # # # # #             "photo": tenant.photo,
# # # # # # # #             "id_card_number": tenant.id_card_number,
# # # # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # # # #             "balance": tenant.balance,
# # # # # # # #             "created_at": tenant.created_at,
# # # # # # # #             "updated_at": tenant.updated_at,
# # # # # # # #             "is_active": tenant.is_active,
# # # # # # # #             "room_number": room_number
# # # # # # # #         }
# # # # # # # #         result.append(tenant_dict)
    
# # # # # # # #     return result


# # # # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # # # #     """Update tenant information"""
# # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # #     if not db_tenant:
# # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # #     if 'guardian_phone' in kwargs:
# # # # # # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # # # # # #     for key, value in kwargs.items():
# # # # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # # # #             setattr(db_tenant, key, value)
    
# # # # # # # #     db.commit()
# # # # # # # #     db.refresh(db_tenant)
    
# # # # # # # #     return db_tenant


# # # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # # # #     """Assign tenant to a room"""
# # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # #     if not tenant:
# # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # # #     if not room:
# # # # # # # #         raise ValueError("Room not found")
    
# # # # # # # #     if room.is_occupied:
# # # # # # # #         raise ValueError("Room is already occupied")
    
# # # # # # # #     tenant.assigned_room_id = room_id
# # # # # # # #     tenant.balance = room.rent_amount
# # # # # # # #     room.is_occupied = True
    
# # # # # # # #     db.commit()
# # # # # # # #     db.refresh(tenant)
    
# # # # # # # #     return tenant


# # # # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # # # #     """Get all archived tenants for a landlord"""
# # # # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # # # #     return archived


# # # # # # # # # # app/crud/tenant.py - FINAL WORKING VERSION
# # # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # # from sqlalchemy import func
# # # # # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # # # # from app.schemas import TenantCreate
# # # # # # # # # from datetime import datetime

# # # # # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # # # # #     """Create a new tenant"""
# # # # # # # # #     db_tenant = Tenant(
# # # # # # # # #         full_name=tenant.full_name,
# # # # # # # # #         phone_number=tenant.phone_number,
# # # # # # # # #         email=tenant.email,
# # # # # # # # #         id_card_number=tenant.id_card_number,
# # # # # # # # #         faculty=tenant.faculty,
# # # # # # # # #         year_of_study=tenant.year_of_study,
# # # # # # # # #         guardian_name=tenant.guardian_name,
# # # # # # # # #         guardian_phone_number=tenant.guardian_phone_number,
# # # # # # # # #         guardian_location=tenant.guardian_location,
# # # # # # # # #         is_active=True,
# # # # # # # # #         balance=0.0
# # # # # # # # #     )
# # # # # # # # #     db.add(db_tenant)
# # # # # # # # #     db.commit()
# # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # #     return db_tenant


# # # # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # # # #     """Vacate tenant and archive their data"""
# # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # #     if not db_tenant:
# # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # #     # Get room and landlord info
# # # # # # # # #     room_info = None
# # # # # # # # #     landlord_id_val = None
# # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # #         if room:
# # # # # # # # #             room_info = room.room_number
# # # # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # # # #     # Create archived record
# # # # # # # # #     db_archived = ArchivedTenant(
# # # # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # # # #         landlord_id=landlord_id_val,
# # # # # # # # #         full_name=db_tenant.full_name,
# # # # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # # # #         email=db_tenant.email,
# # # # # # # # #         room_number=room_info,
# # # # # # # # #         final_balance=db_tenant.balance,
# # # # # # # # #         archived_at=func.now()
# # # # # # # # #     )
    
# # # # # # # # #     db.add(db_archived)
    
# # # # # # # # #     # Clear room assignment
# # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # #         if room:
# # # # # # # # #             room.is_occupied = False
    
# # # # # # # # #     db_tenant.assigned_room_id = None
# # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # #     db.commit()
# # # # # # # # #     db.refresh(db_archived)
    
# # # # # # # # #     return db_archived


# # # # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # # # #     """Deactivate a tenant"""
# # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # #     if not db_tenant:
# # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # #         if room:
# # # # # # # # #             room.is_occupied = False
# # # # # # # # #         db_tenant.assigned_room_id = None
    
# # # # # # # # #     db.commit()
# # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # #     return db_tenant


# # # # # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # # # # #     """Get tenant with room information"""
# # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # #     if not tenant:
# # # # # # # # #         return None
    
# # # # # # # # #     landlord_id_val = None
# # # # # # # # #     room_number = None
# # # # # # # # #     property_name = None
# # # # # # # # #     room_rent = None
    
# # # # # # # # #     if tenant.assigned_room_id:
# # # # # # # # #         room = db.query(Room).join(Property).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # # #         if room:
# # # # # # # # #             room_number = room.room_number
# # # # # # # # #             room_rent = room.rent_amount
# # # # # # # # #             property_name = room.property.property_name
# # # # # # # # #             landlord_id_val = room.property.landlord_id
    
# # # # # # # # #     return {
# # # # # # # # #         "tenant_id": tenant.tenant_id,
# # # # # # # # #         "landlord_id": landlord_id_val,
# # # # # # # # #         "full_name": tenant.full_name,
# # # # # # # # #         "phone_number": tenant.phone_number,
# # # # # # # # #         "email": tenant.email,
# # # # # # # # #         "id_card_number": tenant.id_card_number,
# # # # # # # # #         "faculty": tenant.faculty,
# # # # # # # # #         "year_of_study": tenant.year_of_study,
# # # # # # # # #         "guardian_name": tenant.guardian_name,
# # # # # # # # #         "guardian_phone": tenant.guardian_phone_number,
# # # # # # # # #         "guardian_location": tenant.guardian_location,
# # # # # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # #         "balance": tenant.balance,
# # # # # # # # #         "is_active": tenant.is_active,
# # # # # # # # #         "created_at": tenant.created_at,
# # # # # # # # #         "room_number": room_number,
# # # # # # # # #         "property_name": property_name,
# # # # # # # # #         "room_rent": room_rent
# # # # # # # # #     }


# # # # # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # # # # #     """Get all active tenants for a landlord"""
# # # # # # # # #     # Get tenants through rooms and properties
# # # # # # # # #     tenants = db.query(Tenant).join(
# # # # # # # # #         Room, Tenant.assigned_room_id == Room.room_id
# # # # # # # # #     ).join(
# # # # # # # # #         Property, Room.property_id == Property.property_id
# # # # # # # # #     ).filter(
# # # # # # # # #         Property.landlord_id == landlord_id,
# # # # # # # # #         Tenant.is_active == True
# # # # # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # # # # #     result = []
# # # # # # # # #     for tenant in tenants:
# # # # # # # # #         tenant_data = {
# # # # # # # # #             "tenant_id": tenant.tenant_id,
# # # # # # # # #             "full_name": tenant.full_name,
# # # # # # # # #             "phone_number": tenant.phone_number,
# # # # # # # # #             "email": tenant.email,
# # # # # # # # #             "balance": tenant.balance,
# # # # # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # #             "room_number": None
# # # # # # # # #         }
        
# # # # # # # # #         if tenant.assigned_room_id:
# # # # # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # # #             if room:
# # # # # # # # #                 tenant_data["room_number"] = room.room_number
        
# # # # # # # # #         result.append(tenant_data)
    
# # # # # # # # #     return result


# # # # # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # # # # #     """Update tenant information"""
# # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # #     if not db_tenant:
# # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # #     # Map guardian_phone to guardian_phone_number if provided
# # # # # # # # #     if 'guardian_phone' in kwargs:
# # # # # # # # #         kwargs['guardian_phone_number'] = kwargs.pop('guardian_phone')
    
# # # # # # # # #     # Update only provided fields
# # # # # # # # #     for key, value in kwargs.items():
# # # # # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # # # # #             setattr(db_tenant, key, value)
    
# # # # # # # # #     db.commit()
# # # # # # # # #     db.refresh(db_tenant)
    
# # # # # # # # #     return db_tenant


# # # # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # # # # #     """Assign tenant to a room"""
# # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # #     if not tenant:
# # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # # # #     if not room:
# # # # # # # # #         raise ValueError("Room not found")
    
# # # # # # # # #     if room.is_occupied:
# # # # # # # # #         raise ValueError("Room is already occupied")
    
# # # # # # # # #     tenant.assigned_room_id = room_id
# # # # # # # # #     tenant.balance = room.rent_amount
# # # # # # # # #     room.is_occupied = True
    
# # # # # # # # #     db.commit()
# # # # # # # # #     db.refresh(tenant)
    
# # # # # # # # #     return tenant


# # # # # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # # # # #     """Get all archived tenants for a landlord"""
# # # # # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # # # # #     return archived


# # # # # # # # # # # app/crud/tenant.py - SIMPLIFIED VERSION
# # # # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # # # from sqlalchemy import func
# # # # # # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # # # # # from app.schemas import TenantCreate
# # # # # # # # # # from datetime import datetime

# # # # # # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # # # # # #     """Create a new tenant"""
# # # # # # # # # #     db_tenant = Tenant(
# # # # # # # # # #         landlord_id=landlord_id,
# # # # # # # # # #         full_name=tenant.full_name,
# # # # # # # # # #         phone_number=tenant.phone_number,
# # # # # # # # # #         email=tenant.email,
# # # # # # # # # #         id_card_number=tenant.id_card_number,
# # # # # # # # # #         faculty=tenant.faculty,
# # # # # # # # # #         year_of_study=tenant.year_of_study,
# # # # # # # # # #         guardian_name=tenant.guardian_name,
# # # # # # # # # #         guardian_phone=tenant.guardian_phone,
# # # # # # # # # #         guardian_location=tenant.guardian_location,
# # # # # # # # # #         is_active=True,
# # # # # # # # # #         balance=0.0
# # # # # # # # # #     )
# # # # # # # # # #     db.add(db_tenant)
# # # # # # # # # #     db.commit()
# # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # #     return db_tenant


# # # # # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # # # # #     """Vacate tenant and archive their data"""
# # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # #     if not db_tenant:
# # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # #     # Get room info before vacating
# # # # # # # # # #     room_info = None
# # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # #         if room:
# # # # # # # # # #             room_info = room.room_number
    
# # # # # # # # # #     # Create archived record - ONLY fields that exist in ArchivedTenant model
# # # # # # # # # #     db_archived = ArchivedTenant(
# # # # # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # # # # #         landlord_id=db_tenant.landlord_id,
# # # # # # # # # #         full_name=db_tenant.full_name,
# # # # # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # # # # #         email=db_tenant.email,
# # # # # # # # # #         room_number=room_info,
# # # # # # # # # #         final_balance=db_tenant.balance,
# # # # # # # # # #         archived_at=func.now()
# # # # # # # # # #     )
    
# # # # # # # # # #     db.add(db_archived)
    
# # # # # # # # # #     # Clear room assignment
# # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # #         if room:
# # # # # # # # # #             room.is_occupied = False
    
# # # # # # # # # #     db_tenant.assigned_room_id = None
# # # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # # #     db.commit()
# # # # # # # # # #     db.refresh(db_archived)
    
# # # # # # # # # #     return db_archived


# # # # # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # # # # #     """Deactivate a tenant (existing function - keep as is)"""
# # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # #     if not db_tenant:
# # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # #         if room:
# # # # # # # # # #             room.is_occupied = False
# # # # # # # # # #         db_tenant.assigned_room_id = None
    
# # # # # # # # # #     db.commit()
# # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # #     return db_tenant


# # # # # # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # # # # # #     """Get tenant with room information"""
# # # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # #     if not tenant:
# # # # # # # # # #         return None
    
# # # # # # # # # #     # Convert to dict and add room_number if assigned
# # # # # # # # # #     tenant_dict = {
# # # # # # # # # #         "tenant_id": tenant.tenant_id,
# # # # # # # # # #         "landlord_id": tenant.landlord_id,
# # # # # # # # # #         "full_name": tenant.full_name,
# # # # # # # # # #         "phone_number": tenant.phone_number,
# # # # # # # # # #         "email": tenant.email,
# # # # # # # # # #         "id_card_number": tenant.id_card_number,
# # # # # # # # # #         "faculty": tenant.faculty,
# # # # # # # # # #         "year_of_study": tenant.year_of_study,
# # # # # # # # # #         "guardian_name": tenant.guardian_name,
# # # # # # # # # #         "guardian_phone": tenant.guardian_phone,
# # # # # # # # # #         "guardian_location": tenant.guardian_location,
# # # # # # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # # #         "balance": tenant.balance,
# # # # # # # # # #         "is_active": tenant.is_active,
# # # # # # # # # #         "created_at": tenant.created_at,
# # # # # # # # # #         "room_number": None,
# # # # # # # # # #         "property_name": None,
# # # # # # # # # #         "room_rent": None
# # # # # # # # # #     }
    
# # # # # # # # # #     # Get room details if assigned
# # # # # # # # # #     if tenant.assigned_room_id:
# # # # # # # # # #         room = db.query(Room).join(
# # # # # # # # # #             Property, Room.property_id == Property.property_id
# # # # # # # # # #         ).filter(Room.room_id == tenant.assigned_room_id).first()
        
# # # # # # # # # #         if room:
# # # # # # # # # #             tenant_dict["room_number"] = room.room_number
# # # # # # # # # #             tenant_dict["room_rent"] = room.rent_amount
# # # # # # # # # #             tenant_dict["property_name"] = room.property.property_name if room.property else None
    
# # # # # # # # # #     return tenant_dict


# # # # # # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # # # # # #     """Get all active tenants for a landlord with room info"""
# # # # # # # # # #     tenants = db.query(Tenant).filter(
# # # # # # # # # #         Tenant.landlord_id == landlord_id,
# # # # # # # # # #         Tenant.is_active == True
# # # # # # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # # # # # #     result = []
# # # # # # # # # #     for tenant in tenants:
# # # # # # # # # #         tenant_data = {
# # # # # # # # # #             "tenant_id": tenant.tenant_id,
# # # # # # # # # #             "full_name": tenant.full_name,
# # # # # # # # # #             "phone_number": tenant.phone_number,
# # # # # # # # # #             "email": tenant.email,
# # # # # # # # # #             "balance": tenant.balance,
# # # # # # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # # #             "room_number": None
# # # # # # # # # #         }
        
# # # # # # # # # #         # Get room number if assigned
# # # # # # # # # #         if tenant.assigned_room_id:
# # # # # # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # # # #             if room:
# # # # # # # # # #                 tenant_data["room_number"] = room.room_number
        
# # # # # # # # # #         result.append(tenant_data)
    
# # # # # # # # # #     return result


# # # # # # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # # # # # #     """Update tenant information - takes any keyword arguments"""
# # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # #     if not db_tenant:
# # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # #     # Update only provided fields
# # # # # # # # # #     for key, value in kwargs.items():
# # # # # # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # # # # # #             setattr(db_tenant, key, value)
    
# # # # # # # # # #     db.commit()
# # # # # # # # # #     db.refresh(db_tenant)
    
# # # # # # # # # #     return db_tenant


# # # # # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # # # # # #     """Assign tenant to a room"""
# # # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # #     if not tenant:
# # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # # # # #     if not room:
# # # # # # # # # #         raise ValueError("Room not found")
    
# # # # # # # # # #     if room.is_occupied:
# # # # # # # # # #         raise ValueError("Room is already occupied")
    
# # # # # # # # # #     # Assign tenant
# # # # # # # # # #     tenant.assigned_room_id = room_id
# # # # # # # # # #     tenant.balance = room.rent_amount  # Set initial balance to first month rent
    
# # # # # # # # # #     # Mark room as occupied
# # # # # # # # # #     room.is_occupied = True
    
# # # # # # # # # #     db.commit()
# # # # # # # # # #     db.refresh(tenant)
    
# # # # # # # # # #     return tenant


# # # # # # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # # # # # #     """Get all archived tenants for a landlord"""
# # # # # # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # # # # # #     return archived






# # # # # # # # # # # # app/crud/tenant.py - SIMPLIFIED VERSION
# # # # # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # # # # from sqlalchemy import func
# # # # # # # # # # # from app.models import Tenant, Room, Property, ArchivedTenant
# # # # # # # # # # # from app.schemas import TenantCreate
# # # # # # # # # # # from datetime import datetime

# # # # # # # # # # # def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
# # # # # # # # # # #     """Create a new tenant"""
# # # # # # # # # # #     db_tenant = Tenant(
# # # # # # # # # # #         landlord_id=landlord_id,
# # # # # # # # # # #         full_name=tenant.full_name,
# # # # # # # # # # #         phone_number=tenant.phone_number,
# # # # # # # # # # #         email=tenant.email,
# # # # # # # # # # #         id_card_number=tenant.id_card_number,
# # # # # # # # # # #         faculty=tenant.faculty,
# # # # # # # # # # #         year_of_study=tenant.year_of_study,
# # # # # # # # # # #         guardian_name=tenant.guardian_name,
# # # # # # # # # # #         guardian_phone=tenant.guardian_phone,
# # # # # # # # # # #         guardian_location=tenant.guardian_location,
# # # # # # # # # # #         is_active=True,
# # # # # # # # # # #         balance=0.0
# # # # # # # # # # #     )
# # # # # # # # # # #     db.add(db_tenant)
# # # # # # # # # # #     db.commit()
# # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # #     return db_tenant


# # # # # # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # # # # # #     """Vacate tenant and archive their data"""
# # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # #     if not db_tenant:
# # # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # # #     # Get room info before vacating
# # # # # # # # # # #     room_info = None
# # # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # # #         if room:
# # # # # # # # # # #             room_info = room.room_number
    
# # # # # # # # # # #     # Create archived record - ONLY fields that exist in ArchivedTenant model
# # # # # # # # # # #     db_archived = ArchivedTenant(
# # # # # # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # # # # # #         landlord_id=db_tenant.landlord_id,
# # # # # # # # # # #         full_name=db_tenant.full_name,
# # # # # # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # # # # # #         email=db_tenant.email,
# # # # # # # # # # #         room_number=room_info,
# # # # # # # # # # #         final_balance=db_tenant.balance,
# # # # # # # # # # #         archived_at=func.now()
# # # # # # # # # # #     )
    
# # # # # # # # # # #     db.add(db_archived)
    
# # # # # # # # # # #     # Clear room assignment
# # # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # # #         if room:
# # # # # # # # # # #             room.is_occupied = False
    
# # # # # # # # # # #     db_tenant.assigned_room_id = None
# # # # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # # # #     db.commit()
# # # # # # # # # # #     db.refresh(db_archived)
    
# # # # # # # # # # #     return db_archived


# # # # # # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # # # # # #     """Deactivate a tenant (existing function - keep as is)"""
# # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # #     if not db_tenant:
# # # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # # #     db_tenant.is_active = False
    
# # # # # # # # # # #     if db_tenant.assigned_room_id:
# # # # # # # # # # #         room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
# # # # # # # # # # #         if room:
# # # # # # # # # # #             room.is_occupied = False
# # # # # # # # # # #         db_tenant.assigned_room_id = None
    
# # # # # # # # # # #     db.commit()
# # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # #     return db_tenant


# # # # # # # # # # # def get_tenant(db: Session, tenant_id: int):
# # # # # # # # # # #     """Get tenant with room information"""
# # # # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # #     if not tenant:
# # # # # # # # # # #         return None
    
# # # # # # # # # # #     # Convert to dict and add room_number if assigned
# # # # # # # # # # #     tenant_dict = {
# # # # # # # # # # #         "tenant_id": tenant.tenant_id,
# # # # # # # # # # #         "landlord_id": tenant.landlord_id,
# # # # # # # # # # #         "full_name": tenant.full_name,
# # # # # # # # # # #         "phone_number": tenant.phone_number,
# # # # # # # # # # #         "email": tenant.email,
# # # # # # # # # # #         "id_card_number": tenant.id_card_number,
# # # # # # # # # # #         "faculty": tenant.faculty,
# # # # # # # # # # #         "year_of_study": tenant.year_of_study,
# # # # # # # # # # #         "guardian_name": tenant.guardian_name,
# # # # # # # # # # #         "guardian_phone": tenant.guardian_phone,
# # # # # # # # # # #         "guardian_location": tenant.guardian_location,
# # # # # # # # # # #         "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # # # #         "balance": tenant.balance,
# # # # # # # # # # #         "is_active": tenant.is_active,
# # # # # # # # # # #         "created_at": tenant.created_at,
# # # # # # # # # # #         "room_number": None,
# # # # # # # # # # #         "property_name": None,
# # # # # # # # # # #         "room_rent": None
# # # # # # # # # # #     }
    
# # # # # # # # # # #     # Get room details if assigned
# # # # # # # # # # #     if tenant.assigned_room_id:
# # # # # # # # # # #         room = db.query(Room).join(
# # # # # # # # # # #             Property, Room.property_id == Property.property_id
# # # # # # # # # # #         ).filter(Room.room_id == tenant.assigned_room_id).first()
        
# # # # # # # # # # #         if room:
# # # # # # # # # # #             tenant_dict["room_number"] = room.room_number
# # # # # # # # # # #             tenant_dict["room_rent"] = room.rent_amount
# # # # # # # # # # #             tenant_dict["property_name"] = room.property.property_name if room.property else None
    
# # # # # # # # # # #     return tenant_dict


# # # # # # # # # # # def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
# # # # # # # # # # #     """Get all active tenants for a landlord with room info"""
# # # # # # # # # # #     tenants = db.query(Tenant).filter(
# # # # # # # # # # #         Tenant.landlord_id == landlord_id,
# # # # # # # # # # #         Tenant.is_active == True
# # # # # # # # # # #     ).offset(skip).limit(limit).all()
    
# # # # # # # # # # #     result = []
# # # # # # # # # # #     for tenant in tenants:
# # # # # # # # # # #         tenant_data = {
# # # # # # # # # # #             "tenant_id": tenant.tenant_id,
# # # # # # # # # # #             "full_name": tenant.full_name,
# # # # # # # # # # #             "phone_number": tenant.phone_number,
# # # # # # # # # # #             "email": tenant.email,
# # # # # # # # # # #             "balance": tenant.balance,
# # # # # # # # # # #             "assigned_room_id": tenant.assigned_room_id,
# # # # # # # # # # #             "room_number": None
# # # # # # # # # # #         }
        
# # # # # # # # # # #         # Get room number if assigned
# # # # # # # # # # #         if tenant.assigned_room_id:
# # # # # # # # # # #             room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
# # # # # # # # # # #             if room:
# # # # # # # # # # #                 tenant_data["room_number"] = room.room_number
        
# # # # # # # # # # #         result.append(tenant_data)
    
# # # # # # # # # # #     return result


# # # # # # # # # # # def update_tenant(db: Session, tenant_id: int, **kwargs):
# # # # # # # # # # #     """Update tenant information - takes any keyword arguments"""
# # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # #     if not db_tenant:
# # # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # # #     # Update only provided fields
# # # # # # # # # # #     for key, value in kwargs.items():
# # # # # # # # # # #         if hasattr(db_tenant, key) and value is not None:
# # # # # # # # # # #             setattr(db_tenant, key, value)
    
# # # # # # # # # # #     db.commit()
# # # # # # # # # # #     db.refresh(db_tenant)
    
# # # # # # # # # # #     return db_tenant


# # # # # # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
# # # # # # # # # # #     """Assign tenant to a room"""
# # # # # # # # # # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # #     if not tenant:
# # # # # # # # # # #         raise ValueError("Tenant not found")
    
# # # # # # # # # # #     room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # # # # # #     if not room:
# # # # # # # # # # #         raise ValueError("Room not found")
    
# # # # # # # # # # #     if room.is_occupied:
# # # # # # # # # # #         raise ValueError("Room is already occupied")
    
# # # # # # # # # # #     # Assign tenant
# # # # # # # # # # #     tenant.assigned_room_id = room_id
# # # # # # # # # # #     tenant.balance = room.rent_amount  # Set initial balance to first month rent
    
# # # # # # # # # # #     # Mark room as occupied
# # # # # # # # # # #     room.is_occupied = True
    
# # # # # # # # # # #     db.commit()
# # # # # # # # # # #     db.refresh(tenant)
    
# # # # # # # # # # #     return tenant


# # # # # # # # # # # def get_archived_tenants(db: Session, landlord_id: int):
# # # # # # # # # # #     """Get all archived tenants for a landlord"""
# # # # # # # # # # #     archived = db.query(ArchivedTenant).filter(
# # # # # # # # # # #         ArchivedTenant.landlord_id == landlord_id
# # # # # # # # # # #     ).order_by(ArchivedTenant.archived_at.desc()).all()
    
# # # # # # # # # # #     return archived










# # # # # # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # # # # # from ..models import Tenant, ArchivedTenant, Room
# # # # # # # # # # # # from ..schemas import TenantCreate
# # # # # # # # # # # # from sqlalchemy.sql import func

# # # # # # # # # # # # def create_tenant(db: Session, tenant: TenantCreate):
# # # # # # # # # # # #     db_tenant = Tenant(**tenant.dict())
# # # # # # # # # # # #     db.add(db_tenant)
# # # # # # # # # # # #     db.commit()
# # # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # # #     return db_tenant

# # # # # # # # # # # # def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int, rent_amount: float, due_date: int):
# # # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # # #     db_room = db.query(Room).filter(Room.room_id == room_id).first()
# # # # # # # # # # # #     if not db_tenant or not db_room:
# # # # # # # # # # # #         return None
# # # # # # # # # # # #     db_tenant.assigned_room_id = room_id
# # # # # # # # # # # #     db_tenant.balance = rent_amount
# # # # # # # # # # # #     db_room.due_date = due_date
# # # # # # # # # # # #     db.commit()
# # # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # # #     return db_tenant

# # # # # # # # # # # # def deactivate_tenant(db: Session, tenant_id: int):
# # # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # # #     if not db_tenant:
# # # # # # # # # # # #         return None
# # # # # # # # # # # #     db_tenant.is_active = False
# # # # # # # # # # # #     db.commit()
# # # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # # #     return db_tenant

# # # # # # # # # # # # def vacate_and_archive_tenant(db: Session, tenant_id: int):
# # # # # # # # # # # #     db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
# # # # # # # # # # # #     if not db_tenant:
# # # # # # # # # # # #         return None
# # # # # # # # # # # #     # Archive
# # # # # # # # # # # #     db_archived = ArchivedTenant(
# # # # # # # # # # # #         original_tenant_id=db_tenant.tenant_id,
# # # # # # # # # # # #         full_name=db_tenant.full_name,
# # # # # # # # # # # #         phone_number=db_tenant.phone_number,
# # # # # # # # # # # #         email=db_tenant.email,
# # # # # # # # # # # #         faculty=db_tenant.faculty,
# # # # # # # # # # # #         year_of_study=db_tenant.year_of_study,
# # # # # # # # # # # #         guardian_phone_number=db_tenant.guardian_phone_number,
# # # # # # # # # # # #         guardian_name=db_tenant.guardian_name,
# # # # # # # # # # # #         guardian_location=db_tenant.guardian_location,
# # # # # # # # # # # #         photo=db_tenant.photo,
# # # # # # # # # # # #         id_card_number=db_tenant.id_card_number,
# # # # # # # # # # # #         balance=db_tenant.balance,
# # # # # # # # # # # #         archived_at=func.now()
# # # # # # # # # # # #     )
# # # # # # # # # # # #     db.add(db_archived)
# # # # # # # # # # # #     # Vacate
# # # # # # # # # # # #     db_tenant.assigned_room_id = None
# # # # # # # # # # # #     db_tenant.is_active = False
# # # # # # # # # # # #     db.commit()
# # # # # # # # # # # #     db.refresh(db_tenant)
# # # # # # # # # # # #     db.refresh(db_archived)
# # # # # # # # # # # #     return db_archived