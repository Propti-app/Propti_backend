from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import (
    Report, RentCycle, Room, Property, Tenant, Payment,
    PaymentStatus, ArchivedTenant,
)
from app.schemas import ReportCreate
from datetime import date


def create_report(db: Session, landlord_id: int, report: ReportCreate):
    rent_cycles = db.query(RentCycle).join(
        Room, RentCycle.room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        RentCycle.start_date >= report.start_date,
        RentCycle.end_date <= report.end_date,
    ).all()

    total_expected_rent = sum(rc.amount for rc in rent_cycles)
    total_paid = sum(
        sum(p.amount for p in rc.payments)
        for rc in rent_cycles
    )
    total_outstanding = total_expected_rent - total_paid

    db_report = Report(
        landlord_id=landlord_id,
        rent_cycle_id=report.rent_cycle_id,
        start_date=report.start_date,
        end_date=report.end_date,
        total_expected_rent=total_expected_rent,
        total_paid=total_paid,
        total_outstanding=total_outstanding,
        net_income=total_paid,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_dashboard(db: Session, landlord_id: int):
    """Legacy basic dashboard — kept for backward compatibility."""
    properties = db.query(Property).filter(
        Property.landlord_id == landlord_id,
        Property.is_active == True,
    ).all()

    rooms = db.query(Room).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).all()

    total_rooms = len(rooms)
    paid_rooms    = sum(1 for r in rooms if r.payment_status == PaymentStatus.PAID)
    partial_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.PARTIAL)
    overdue_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.OVERDUE)

    return {
        "properties": properties,
        "total_rooms": total_rooms,
        "paid_rooms": paid_rooms,
        "partial_rooms": partial_rooms,
        "overdue_rooms": overdue_rooms,
    }


def get_enhanced_dashboard(db: Session, landlord_id: int):
    """Enhanced dashboard with comprehensive metrics."""
    properties = db.query(Property).filter(
        Property.landlord_id == landlord_id,
        Property.is_active == True,
    ).all()

    rooms = db.query(Room).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).all()

    active_tenants = db.query(Tenant).join(
        Room, Tenant.assigned_room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True,
        Tenant.assigned_room_id.isnot(None),
    ).all()

    expected_rent = db.query(func.sum(Room.rent_amount)).join(
        Property, Room.property_id == Property.property_id
    ).join(
        Tenant, Room.room_id == Tenant.assigned_room_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True,
    ).scalar() or 0.0

    total_paid = db.query(func.sum(Payment.amount)).join(
        RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
    ).join(
        Room, RentCycle.room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).scalar() or 0.0

    outstanding_balance = db.query(func.sum(Tenant.balance)).join(
        Room, Tenant.assigned_room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True,
        Tenant.balance > 0,
    ).scalar() or 0.0

    total_rooms   = len(rooms)
    paid_rooms    = sum(1 for r in rooms if r.payment_status == PaymentStatus.PAID)
    partial_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.PARTIAL)
    overdue_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.OVERDUE)

    property_metrics = []
    for prop in properties:
        prop_rooms = [r for r in rooms if r.property_id == prop.property_id]
        prop_room_ids = {r.room_id for r in prop_rooms}
        prop_tenants = [t for t in active_tenants if t.assigned_room_id in prop_room_ids]

        property_metrics.append({
            "property_id": prop.property_id,
            "property_name": prop.name,
            "total_rooms": len(prop_rooms),
            "total_tenants": len(prop_tenants),
            "paid_rooms":    sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.PAID),
            "partial_rooms": sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.PARTIAL),
            "overdue_rooms": sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.OVERDUE),
        })

    return {
        "expected_rent": expected_rent,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "total_tenants": len(active_tenants),
        "properties": properties,
        "total_rooms": total_rooms,
        "paid_rooms": paid_rooms,
        "partial_rooms": partial_rooms,
        "overdue_rooms": overdue_rooms,
        "property_metrics": property_metrics,
    }


def get_archived_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    """Get archived tenants for a landlord — direct filter, no broken joins."""
    return db.query(ArchivedTenant).filter(
        ArchivedTenant.landlord_id == landlord_id
    ).order_by(ArchivedTenant.archived_at.desc()).offset(skip).limit(limit).all()








