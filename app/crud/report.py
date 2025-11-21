from sqlalchemy.orm import Session
from ..models import Report, RentCycle, Room, Property
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

def get_dashboard(db: Session, landlord_id: int):
    properties = db.query(Property).filter(Property.landlord_id == landlord_id).all()
    rooms = db.query(Room).join(
        Property, Room.property_id == Property.property_id
    ).filter(
        Property.landlord_id == landlord_id
    ).all()
    
    total_rooms = len(rooms)
    paid_rooms = sum(1 for r in rooms if r.payment_status == "Paid")
    partial_rooms = sum(1 for r in rooms if r.payment_status == "Partial")
    overdue_rooms = sum(1 for r in rooms if r.payment_status == "Overdue")
    
    return {
        "properties": properties,
        "total_rooms": total_rooms,
        "paid_rooms": paid_rooms,
        "partial_rooms": partial_rooms,
        "overdue_rooms": overdue_rooms
    }