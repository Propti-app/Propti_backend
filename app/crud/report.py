# app/crud/report.py - ENHANCED VERSION
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import (
    Report, RentCycle, Room, Property, Tenant, Payment, 
    PaymentStatus
)
from ..schemas import ReportCreate
from datetime import date

def create_report(db: Session, landlord_id: int, report: ReportCreate):
    rent_cycles = db.query(RentCycle).join(
        Room, RentCycle.room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        RentCycle.start_date >= report.start_date,
        RentCycle.end_date <= report.end_date
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
        net_income=total_paid
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_enhanced_dashboard(db: Session, landlord_id: int):
    """
    Enhanced dashboard with comprehensive metrics for Cameroonian landlords
    """
    # Get all properties for this landlord
    properties = db.query(Property).filter(
        Property.landlord_id == landlord_id,
        Property.is_active == True
    ).all()
    
    # Get all rooms for this landlord
    rooms = db.query(Room).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).all()
    
    # Get all active tenants
    active_tenants = db.query(Tenant).join(
        Room, Tenant.assigned_room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True,
        Tenant.assigned_room_id.isnot(None)
    ).all()
    
    # Calculate expected rent (aggregate of all assigned room rents)
    expected_rent = db.query(func.sum(Room.rent_amount)).join(
        Property, Room.property_id == Property.property_id
    ).join(
        Tenant, Room.room_id == Tenant.assigned_room_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True
    ).scalar() or 0.0
    
    # Calculate total paid (all payments made)
    total_paid = db.query(func.sum(Payment.amount)).join(
        RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
    ).join(
        Room, RentCycle.room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).scalar() or 0.0
    
    # Calculate outstanding balance (sum of all tenant balances)
    outstanding_balance = db.query(func.sum(Tenant.balance)).join(
        Room, Tenant.assigned_room_id == Room.room_id
    ).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id,
        Tenant.is_active == True,
        Tenant.balance > 0
    ).scalar() or 0.0
    
    # Count rooms by payment status
    total_rooms = len(rooms)
    paid_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.PAID)
    partial_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.PARTIAL)
    overdue_rooms = sum(1 for r in rooms if r.payment_status == PaymentStatus.OVERDUE)
    
    # Property-specific metrics
    property_metrics = []
    for prop in properties:
        prop_rooms = [r for r in rooms if r.property_id == prop.property_id]
        prop_tenants = [t for t in active_tenants if any(
            r.room_id == t.assigned_room_id for r in prop_rooms
        )]
        
        property_metrics.append({
            'property_id': prop.property_id,
            'property_name': prop.name,
            'total_rooms': len(prop_rooms),
            'total_tenants': len(prop_tenants),
            'paid_rooms': sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.PAID),
            'partial_rooms': sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.PARTIAL),
            'overdue_rooms': sum(1 for r in prop_rooms if r.payment_status == PaymentStatus.OVERDUE)
        })
    
    return {
        # Main KPI cards (top row)
        "expected_rent": expected_rent,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "total_tenants": len(active_tenants),
        
        # Property list
        "properties": properties,
        
        # Overall room metrics
        "total_rooms": total_rooms,
        "paid_rooms": paid_rooms,
        "partial_rooms": partial_rooms,
        "overdue_rooms": overdue_rooms,
        
        # Per-property breakdown
        "property_metrics": property_metrics
    }


def get_archived_tenants(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
    """Get archived tenants for a landlord"""
    from ..models import ArchivedTenant
    
    # Get archived tenants through their original assignments
    archived = db.query(ArchivedTenant).join(
        Tenant, ArchivedTenant.original_tenant_id == Tenant.tenant_id
    ).join(
        Room, Tenant.assigned_room_id == Room.room_id, isouter=True
    ).join(
        Property, Room.property_id == Property.property_id, isouter=True
    ).filter(
        Property.landlord_id == landlord_id
    ).offset(skip).limit(limit).all()
    
    return archived


# from sqlalchemy.orm import Session
# from ..models import Report, RentCycle, Room, Property
# from ..schemas import ReportCreate
# from datetime import date

# def create_report(db: Session, landlord_id: int, report: ReportCreate):
#     rent_cycles = db.query(RentCycle).join(
#         Room, RentCycle.room_id == Room.room_id
#     ).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Property.landlord_id == landlord_id,
#         RentCycle.start_date >= report.start_date,
#         RentCycle.end_date <= report.end_date
#     ).all()
    
#     total_expected_rent = sum(rc.amount for rc in rent_cycles)
#     total_paid = sum(
#         sum(p.amount for p in rc.payments)
#         for rc in rent_cycles
#     )
#     total_outstanding = total_expected_rent - total_paid
    
#     db_report = Report(
#         landlord_id=landlord_id,
#         rent_cycle_id=report.rent_cycle_id,
#         start_date=report.start_date,
#         end_date=report.end_date,
#         total_expected_rent=total_expected_rent,
#         total_paid=total_paid,
#         total_outstanding=total_outstanding,
#         net_income=total_paid
#     )
#     db.add(db_report)
#     db.commit()
#     db.refresh(db_report)
#     return db_report

# def get_dashboard(db: Session, landlord_id: int):
#     properties = db.query(Property).filter(Property.landlord_id == landlord_id).all()
#     rooms = db.query(Room).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Property.landlord_id == landlord_id
#     ).all()
    
#     total_rooms = len(rooms)
#     paid_rooms = sum(1 for r in rooms if r.payment_status == "Paid")
#     partial_rooms = sum(1 for r in rooms if r.payment_status == "Partial")
#     overdue_rooms = sum(1 for r in rooms if r.payment_status == "Overdue")
    
#     return {
#         "properties": properties,
#         "total_rooms": total_rooms,
#         "paid_rooms": paid_rooms,
#         "partial_rooms": partial_rooms,
#         "overdue_rooms": overdue_rooms
#     }