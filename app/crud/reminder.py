from sqlalchemy.orm import Session
from ..models import Reminder, Tenant, RentCycle
from datetime import datetime, date
from ..schemas import PaymentStatus

def create_reminder(db: Session, tenant_id: int, message: str, medium: str):
    db_reminder = Reminder(
        tenant_id=tenant_id,
        message=message,
        medium=medium,
        status="Sent"
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def schedule_reminders(db: Session):
    today = date.today()
    tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
    for tenant in tenants:
        if not tenant.assigned_room_id:
            continue
        rent_cycles = db.query(RentCycle).filter(
            RentCycle.tenant_id == tenant.tenant_id,
            RentCycle.payment_status != PaymentStatus.PAID,
            RentCycle.end_date >= today
        ).all()
        for rent_cycle in rent_cycles:
            message = f"Reminder: Rent for {rent_cycle.room.room_number} is due. Balance: {tenant.balance}"
            create_reminder(db, tenant.tenant_id, message, "Email")