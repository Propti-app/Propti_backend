# app/api/routers/payments.py - REPLACE ENTIRE FILE

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.utils.auth import get_current_landlord
from app.models import Payment, RentCycle, Tenant, Room, Property
import urllib.parse
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
def record_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Record a new payment"""
    try:
        db_payment = crud.create_payment(db, payment=payment)
        return db_payment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{tenant_id}")
def get_payment_history(
    tenant_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get payment history for tenant"""
    try:
        history = crud.get_payment_history(db, tenant_id=tenant_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get payment by ID"""
    payment = crud.get_payment_by_id(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/{payment_id}/download-pdf")
async def download_receipt_pdf(
    payment_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Download receipt as PDF"""
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
    room = None
    property_obj = None
    if rent_cycle:
        room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
        if room:
            property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
            if not property_obj or property_obj.landlord_id != landlord.landlord_id:
                raise HTTPException(status_code=403, detail="Not authorized")
    
    payment_data = {
        'receipt_number': payment.receipt_number,
        'tenant_name': tenant.full_name if tenant else "Unknown",
        'room_number': room.room_number if room else "N/A",
        'amount': payment.amount,
        'payment_date': payment.payment_date,
        'payment_method': payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
        'period_start': str(payment.period_start) if payment.period_start else "N/A",
        'period_end': str(payment.period_end) if payment.period_end else "N/A",
        'remaining_balance': tenant.balance if tenant else 0,
        'landlord_name': landlord.name,
        'landlord_contact': landlord.phone_number
    }
    
    try:
        from app.utils.pdf_generator import generate_payment_receipt
        pdf_buffer = generate_payment_receipt(payment_data)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"
            }
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF library not installed. Run: pip install reportlab")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


@router.post("/{payment_id}/share-whatsapp")
async def share_whatsapp(
    payment_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get WhatsApp share URL"""
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
    room = None
    if rent_cycle:
        room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
    payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
    message = (
        f"*PAYMENT RECEIPT*\n\n"
        f"Receipt No: {payment.receipt_number}\n"
        f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
        f"Room: {room.room_number if room else 'N/A'}\n\n"
        f"Amount Paid: {int(payment.amount):,} FCFA\n"
        f"Payment Date: {payment_date_str}\n"
        f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
        f"Period: {payment.period_start} to {payment.period_end}\n\n"
        f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n"
        f"Status: {'PAID IN FULL' if (tenant and tenant.balance == 0) else 'PARTIALLY PAID'}\n\n"
        f"Landlord: {landlord.name}\n"
        f"Contact: {landlord.phone_number}\n\n"
        f"Thank you!"
    )
    
    phone = tenant.phone_number if tenant else ""
    phone = ''.join(filter(str.isdigit, phone))
    if not phone.startswith('237'):
        phone = '237' + phone
    
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    return {
        "success": True,
        "url": whatsapp_url,
        "phone": phone
    }


@router.post("/{payment_id}/share-email")
async def share_email(
    payment_id: int,
    db: Session = Depends(get_db),
    landlord = Depends(get_current_landlord)
):
    """Get Email mailto URL"""
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
    room = None
    if rent_cycle:
        room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
    payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
    subject = f"Payment Receipt - {payment.receipt_number}"
    
    body = (
        f"PAYMENT RECEIPT\n\n"
        f"Receipt No: {payment.receipt_number}\n"
        f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
        f"Room: {room.room_number if room else 'N/A'}\n\n"
        f"Amount Paid: {int(payment.amount):,} FCFA\n"
        f"Payment Date: {payment_date_str}\n"
        f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
        f"Period: {payment.period_start} to {payment.period_end}\n\n"
        f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n\n"
        f"Landlord: {landlord.name}\n"
        f"Contact: {landlord.phone_number}"
    )
    
    email = tenant.email if tenant and tenant.email else ""
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    
    mailto_url = f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
    
    return {
        "success": True,
        "url": mailto_url,
        "email": email
    }




