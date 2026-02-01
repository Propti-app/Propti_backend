# app/crud/payment.py - RETURNS DICTIONARIES NOT OBJECTS
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Payment, RentCycle, Tenant, Room, Property, Landlord
from app.schemas import PaymentCreate
from datetime import datetime

def create_payment(db: Session, payment: PaymentCreate):
    """Create a new payment and update tenant balance"""
    db_payment = Payment(
        rent_cycle_id=payment.rent_cycle_id,
        tenant_id=payment.tenant_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_date=func.now(),
        period_start=payment.period_start,
        period_end=payment.period_end
    )
    
    db.add(db_payment)
    
    # Update tenant balance
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    if tenant:
        tenant.balance = max(0, tenant.balance - payment.amount)
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


def get_payment_history(db: Session, tenant_id: int):
    """Get payment history for a tenant - RETURNS DICTIONARIES"""
    payments = db.query(Payment).filter(
        Payment.tenant_id == tenant_id
    ).order_by(Payment.payment_date.desc()).all()
    
    # Convert to dictionaries
    result = []
    for payment in payments:
        payment_dict = {
            "payment_id": payment.payment_id,
            "rent_cycle_id": payment.rent_cycle_id,
            "tenant_id": payment.tenant_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "period_start": payment.period_start.isoformat() if payment.period_start else None,
            "period_end": payment.period_end.isoformat() if payment.period_end else None,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        }
        result.append(payment_dict)
    
    return {"payments": result}


def get_payment_by_id(db: Session, payment_id: int):
    """Get a specific payment by ID"""
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        return None
    
    # Get related data
    rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    
    room = None
    property_obj = None
    landlord = None
    
    if rent_cycle:
        room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
        if room:
            property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
            if property_obj:
                landlord = db.query(Landlord).filter(Landlord.landlord_id == property_obj.landlord_id).first()
    
    return {
        "payment_id": payment.payment_id,
        "tenant_id": payment.tenant_id,
        "tenant_name": tenant.full_name if tenant else None,
        "amount": payment.amount,
        "payment_method": payment.payment_method,
        "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
        "period_start": payment.period_start.isoformat() if payment.period_start else None,
        "period_end": payment.period_end.isoformat() if payment.period_end else None,
        "room_number": room.room_number if room else None,
        "property_name": property_obj.name if property_obj else None,
        "landlord_name": landlord.full_name if landlord else None,
        "landlord_phone": landlord.phone_number if landlord else None,
        "remaining_balance": tenant.balance if tenant else 0.0
    }




