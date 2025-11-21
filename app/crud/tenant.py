from sqlalchemy.orm import Session
from ..models import Tenant, ArchivedTenant, Room
from ..schemas import TenantCreate
from sqlalchemy.sql import func

def create_tenant(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(**tenant.dict())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def assign_tenant_to_room(db: Session, tenant_id: int, room_id: int, rent_amount: float, due_date: int):
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    db_room = db.query(Room).filter(Room.room_id == room_id).first()
    if not db_tenant or not db_room:
        return None
    db_tenant.assigned_room_id = room_id
    db_tenant.balance = rent_amount
    db_room.due_date = due_date
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def deactivate_tenant(db: Session, tenant_id: int):
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return None
    db_tenant.is_active = False
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def vacate_and_archive_tenant(db: Session, tenant_id: int):
    db_tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not db_tenant:
        return None
    # Archive
    db_archived = ArchivedTenant(
        original_tenant_id=db_tenant.tenant_id,
        full_name=db_tenant.full_name,
        phone_number=db_tenant.phone_number,
        email=db_tenant.email,
        faculty=db_tenant.faculty,
        year_of_study=db_tenant.year_of_study,
        guardian_phone_number=db_tenant.guardian_phone_number,
        guardian_name=db_tenant.guardian_name,
        guardian_location=db_tenant.guardian_location,
        photo=db_tenant.photo,
        id_card_number=db_tenant.id_card_number,
        balance=db_tenant.balance,
        archived_at=func.now()
    )
    db.add(db_archived)
    # Vacate
    db_tenant.assigned_room_id = None
    db_tenant.is_active = False
    db.commit()
    db.refresh(db_tenant)
    db.refresh(db_archived)
    return db_archived