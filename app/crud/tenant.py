from sqlalchemy.orm import Session
from app.models import Tenant, Room, Property, ArchivedTenant
from app.schemas import TenantCreate
from datetime import datetime


def create_tenant(db: Session, tenant: TenantCreate, landlord_id: int):
    """Create a new tenant linked to landlord."""
    db_tenant = Tenant(
        landlord_id=landlord_id,
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
        balance=0.0,
    )
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenant(db: Session, tenant_id: int, landlord_id: int):
    """Get a single tenant — only if they belong to this landlord."""
    tenant = db.query(Tenant).filter(
        Tenant.tenant_id == tenant_id,
        Tenant.landlord_id == landlord_id,
    ).first()

    if not tenant:
        return None

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
        "id_card_url": tenant.id_card_url,
        "faculty": tenant.faculty,
        "year_of_study": tenant.year_of_study,
        "guardian_name": tenant.guardian_name,
        "guardian_phone_number": tenant.guardian_phone_number,
        "guardian_location": tenant.guardian_location,
        "photo": tenant.photo,
        "photo_url": tenant.photo_url,
        "assigned_room_id": tenant.assigned_room_id,
        "balance": tenant.balance,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at,
        "updated_at": tenant.updated_at,
        "agreement_signed": tenant.agreement_signed,
        "agreement_url": tenant.agreement_url,
        "room_number": room_number,
        "property_name": property_name,
        "room_rent": room_rent,
    }


def get_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    """Get all active tenants for this landlord."""
    tenants = db.query(Tenant).filter(
        Tenant.landlord_id == landlord_id,
        Tenant.is_active == True,
    ).offset(skip).limit(limit).all()

    result = []
    for tenant in tenants:
        room_number = None
        if tenant.assigned_room_id:
            room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
            if room:
                room_number = room.room_number

        result.append({
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
            "photo_url": tenant.photo_url,
            "id_card_number": tenant.id_card_number,
            "id_card_url": tenant.id_card_url,
            "assigned_room_id": tenant.assigned_room_id,
            "balance": tenant.balance,
            "created_at": tenant.created_at,
            "updated_at": tenant.updated_at,
            "is_active": tenant.is_active,
            "agreement_signed": tenant.agreement_signed,
            "agreement_url": tenant.agreement_url,
            "room_number": room_number,
        })

    return result


def update_tenant(db: Session, tenant_id: int, **kwargs):
    """Update tenant information."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")

    # Normalise guardian phone key
    if "guardian_phone" in kwargs:
        kwargs["guardian_phone_number"] = kwargs.pop("guardian_phone")

    for key, value in kwargs.items():
        if hasattr(db_tenant, key) and value is not None:
            setattr(db_tenant, key, value)

    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int):
    """Assign a tenant to a room."""
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise ValueError("Tenant not found")

    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        raise ValueError("Room not found")

    if room.is_occupied:
        raise ValueError("Room is already occupied")

    # Vacate previous room if any
    if tenant.assigned_room_id:
        old_room = db.query(Room).filter(Room.room_id == tenant.assigned_room_id).first()
        if old_room:
            old_room.is_occupied = False

    tenant.assigned_room_id = room_id
    tenant.balance = room.rent_amount
    room.is_occupied = True

    db.commit()
    db.refresh(tenant)
    return tenant


def vacate_and_archive_tenant(db: Session, tenant_id: int):
    """Vacate a tenant and move them to the archive."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")

    # Capture room number before unassigning
    room_number = None
    if db_tenant.assigned_room_id:
        room = db.query(Room).filter(Room.room_id == db_tenant.assigned_room_id).first()
        if room:
            room_number = room.room_number
            room.is_occupied = False

    db_archived = ArchivedTenant(
        original_tenant_id=db_tenant.tenant_id,
        landlord_id=db_tenant.landlord_id,
        full_name=db_tenant.full_name,
        phone_number=db_tenant.phone_number,
        email=db_tenant.email,
        room_number=room_number,
        balance=db_tenant.balance,
        agreement_url=db_tenant.agreement_url,
    )

    db.add(db_archived)

    db_tenant.assigned_room_id = None
    db_tenant.is_active = False

    db.commit()
    db.refresh(db_archived)
    return db_archived


def deactivate_tenant(db: Session, tenant_id: int):
    """Soft-delete a tenant without archiving."""
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        raise ValueError("Tenant not found")

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
    """Get all archived tenants for this landlord."""
    return db.query(ArchivedTenant).filter(
        ArchivedTenant.landlord_id == landlord_id
    ).order_by(ArchivedTenant.archived_at.desc()).all()











