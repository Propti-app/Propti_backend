from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from ... import schemas, crud, models
from ...database import get_db
from ...utils.auth import get_current_landlord_id
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=schemas.PaymentResponse)
def create_payment(
    payment: schemas.PaymentCreate,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    rent_cycle = db.query(models.RentCycle).filter(
        models.RentCycle.rent_cycle_id == payment.rent_cycle_id
    ).first()
    if not rent_cycle:
        raise HTTPException(status_code=404, detail="Rent cycle not found")
    room = db.query(models.Room).filter(
        models.Room.room_id == rent_cycle.room_id
    ).first()
    if not room or room.property.landlord_id != landlord_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if payment.tenant_id != rent_cycle.tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not assigned to this rent cycle")
    
    db_payment = crud.create_payment(db, payment)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment creation failed")
    return db_payment

@router.get("/history/{tenant_id}", response_model=schemas.PaymentHistoryResponse)
def get_payment_history(
    tenant_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    tenant = db.query(models.Tenant).filter(
        models.Tenant.tenant_id == tenant_id,
        models.Tenant.is_active == True
    ).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if tenant.assigned_room:
        room = db.query(models.Room).filter(
            models.Room.room_id == tenant.assigned_room_id
        ).first()
        if room.property.landlord_id != landlord_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    payments = crud.get_payment_history(db, tenant_id, skip, limit)
    return {"payments": payments}

@router.get("/{payment_id}/pdf")
def download_receipt_pdf(
    payment_id: int,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).options(
        joinedload(models.Payment.tenant),
        joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
    ).join(
        models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
    ).join(
        models.Room, models.RentCycle.room_id == models.Room.room_id
    ).join(
        models.Property, models.Room.property_id == models.Property.property_id
    ).filter(
        models.Payment.payment_id == payment_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"Receipt: {payment.receipt_number}")
    p.drawString(100, 730, f"Tenant: {payment.tenant.full_name}")
    p.drawString(100, 710, f"Room: {payment.rent_cycle.room.room_number}")
    p.drawString(100, 690, f"Amount Paid: {payment.amount}")
    p.drawString(100, 670, f"Payment Date: {payment.payment_date.strftime('%Y-%m-%d')}")
    p.drawString(100, 650, f"Period: {payment.period_start} to {payment.period_end}")
    p.drawString(100, 630, f"Remaining Balance: {payment.tenant.balance}")
    p.drawString(100, 610, f"Landlord: {payment.rent_cycle.room.property.landlord.name}")
    p.drawString(100, 590, f"Contact: {payment.rent_cycle.room.property.landlord.phone_number}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"}
    )

@router.post("/{payment_id}/share")
def share_receipt(
    payment_id: int,
    medium: str,
    landlord_id: int = Depends(get_current_landlord_id),
    db: Session = Depends(get_db)
):
    payment = db.query(models.Payment).options(
        joinedload(models.Payment.tenant),
        joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
    ).join(
        models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
    ).join(
        models.Room, models.RentCycle.room_id == models.Room.room_id
    ).join(
        models.Property, models.Room.property_id == models.Property.property_id
    ).filter(
        models.Payment.payment_id == payment_id,
        models.Property.landlord_id == landlord_id
    ).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    message = (
        f"Receipt: {payment.receipt_number}\n"
        f"Tenant: {payment.tenant.full_name}\n"
        f"Room: {payment.rent_cycle.room.room_number}\n"
        f"Amount Paid: {payment.amount}\n"
        f"Payment Date: {payment.payment_date.strftime('%Y-%m-%d')}\n"
        f"Period: {payment.period_start} to {payment.period_end}\n"
        f"Remaining Balance: {payment.tenant.balance}\n"
        f"Landlord: {payment.rent_cycle.room.property.landlord.name}\n"
        f"Contact: {payment.rent_cycle.room.property.landlord.phone_number}"
    )
    crud.create_reminder(db, payment.tenant_id, message, medium)
    return {"message": f"Receipt shared via {medium}"}






