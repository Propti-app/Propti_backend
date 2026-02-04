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










# # app/api/routers/payments.py - COMPLETE WITH ALL TENANT INFO

# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from app import crud, schemas
# from app.database import get_db
# from app.utils.auth import get_current_landlord
# from app.models import Payment, RentCycle, Tenant, Room, Property
# import urllib.parse
# from datetime import datetime

# router = APIRouter(prefix="/payments", tags=["payments"])


# @router.post("/")
# def record_payment(
#     payment: schemas.PaymentCreate,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Record payment"""
#     try:
#         db_payment = crud.create_payment(db, payment=payment)
#         return db_payment
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/history/{tenant_id}")
# def get_payment_history(
#     tenant_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get payment history"""
#     try:
#         history = crud.get_payment_history(db, tenant_id=tenant_id)
#         return history
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{payment_id}")
# def get_payment(
#     payment_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get payment"""
#     payment = crud.get_payment_by_id(db, payment_id=payment_id)
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
#     return payment


# @router.get("/{payment_id}/download-pdf")
# async def download_receipt_pdf(
#     payment_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Download receipt PDF with ALL info"""
#     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
    
#     # Get ALL related data
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
#     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
#     room = None
#     property_obj = None
#     if rent_cycle:
#         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
#         if room:
#             property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
#             if not property_obj or property_obj.landlord_id != landlord.landlord_id:
#                 raise HTTPException(status_code=403, detail="Not authorized")
    
#     # Build COMPLETE payment data
#     payment_data = {
#         'receipt_number': payment.receipt_number,
#         # Tenant info
#         'tenant_name': tenant.full_name if tenant else "Unknown",
#         'tenant_phone': tenant.phone_number if tenant else "N/A",
#         'tenant_email': tenant.email if tenant and tenant.email else "N/A",
#         # Room/Property info
#         'room_number': room.room_number if room else "N/A",
#         'property_name': property_obj.name if property_obj else "N/A",
#         # Payment info
#         'amount': payment.amount,
#         'payment_date': payment.payment_date,
#         'payment_method': payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
#         'period_start': str(payment.period_start) if payment.period_start else "N/A",
#         'period_end': str(payment.period_end) if payment.period_end else "N/A",
#         'remaining_balance': tenant.balance if tenant else 0,
#         # Landlord info
#         'landlord_name': landlord.name,
#         'landlord_contact': landlord.phone_number
#     }
    
#     try:
#         from app.utils.pdf_generator import generate_payment_receipt
#         pdf_buffer = generate_payment_receipt(payment_data)
        
#         return StreamingResponse(
#             pdf_buffer,
#             media_type="application/pdf",
#             headers={
#                 "Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"
#             }
#         )
#     except ImportError:
#         raise HTTPException(status_code=500, detail="Install reportlab: pip install reportlab")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


# @router.post("/{payment_id}/share-whatsapp")
# async def share_whatsapp(
#     payment_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get WhatsApp share URL with COMPLETE info"""
#     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
    
#     # Get ALL data
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
#     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
#     room = None
#     property_obj = None
#     if rent_cycle:
#         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
#         if room:
#             property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
    
#     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
#     # COMPLETE message with ALL info
#     message = (
#         f"*PAYMENT RECEIPT*\n\n"
#         f"Receipt No: {payment.receipt_number}\n\n"
#         f"*TENANT INFORMATION*\n"
#         f"Name: {tenant.full_name if tenant else 'Unknown'}\n"
#         f"Phone: {tenant.phone_number if tenant else 'N/A'}\n"
#         f"Email: {tenant.email if tenant and tenant.email else 'N/A'}\n\n"
#         f"*PROPERTY DETAILS*\n"
#         f"Property: {property_obj.name if property_obj else 'N/A'}\n"
#         f"Room: {room.room_number if room else 'N/A'}\n\n"
#         f"*PAYMENT DETAILS*\n"
#         f"Amount Paid: {int(payment.amount):,} FCFA\n"
#         f"Payment Date: {payment_date_str}\n"
#         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
#         f"Period: {payment.period_start} to {payment.period_end}\n\n"
#         f"*BALANCE*\n"
#         f"Remaining: {int(tenant.balance if tenant else 0):,} FCFA\n"
#         f"Status: {'PAID IN FULL' if (tenant and tenant.balance == 0) else 'PARTIALLY PAID'}\n\n"
#         f"*Landlord: {landlord.name}*\n"
#         f"Contact: {landlord.phone_number}\n\n"
#         f"Thank you for your payment!"
#     )
    
#     phone = tenant.phone_number if tenant else ""
#     phone = ''.join(filter(str.isdigit, phone))
#     if not phone.startswith('237'):
#         phone = '237' + phone
    
#     encoded_message = urllib.parse.quote(message)
#     whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
#     return {
#         "success": True,
#         "url": whatsapp_url,
#         "phone": phone
#     }


# @router.post("/{payment_id}/share-email")
# async def share_email(
#     payment_id: int,
#     db: Session = Depends(get_db),
#     landlord = Depends(get_current_landlord)
# ):
#     """Get Email mailto URL"""
#     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
    
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
#     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
#     room = None
#     property_obj = None
#     if rent_cycle:
#         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
#         if room:
#             property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
    
#     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
#     subject = f"Payment Receipt - {payment.receipt_number}"
    
#     body = (
#         f"PAYMENT RECEIPT\n\n"
#         f"Receipt No: {payment.receipt_number}\n\n"
#         f"TENANT INFORMATION\n"
#         f"Name: {tenant.full_name if tenant else 'Unknown'}\n"
#         f"Phone: {tenant.phone_number if tenant else 'N/A'}\n"
#         f"Email: {tenant.email if tenant and tenant.email else 'N/A'}\n\n"
#         f"PROPERTY DETAILS\n"
#         f"Property: {property_obj.name if property_obj else 'N/A'}\n"
#         f"Room: {room.room_number if room else 'N/A'}\n\n"
#         f"PAYMENT DETAILS\n"
#         f"Amount Paid: {int(payment.amount):,} FCFA\n"
#         f"Payment Date: {payment_date_str}\n"
#         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
#         f"Period: {payment.period_start} to {payment.period_end}\n\n"
#         f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n\n"
#         f"Landlord: {landlord.name}\n"
#         f"Contact: {landlord.phone_number}\n\n"
#         f"Thank you for your payment!"
#     )
    
#     email = tenant.email if tenant and tenant.email else ""
#     encoded_subject = urllib.parse.quote(subject)
#     encoded_body = urllib.parse.quote(body)
    
#     mailto_url = f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
    
#     return {
#         "success": True,
#         "url": mailto_url,
#         "email": email
#     }










# # # app/api/routers/payments.py - REPLACE ENTIRE FILE

# # from fastapi import APIRouter, Depends, HTTPException
# # from fastapi.responses import StreamingResponse
# # from sqlalchemy.orm import Session
# # from app import crud, schemas
# # from app.database import get_db
# # from app.utils.auth import get_current_landlord
# # from app.models import Payment, RentCycle, Tenant, Room, Property
# # import urllib.parse
# # from datetime import datetime

# # router = APIRouter(prefix="/payments", tags=["payments"])


# # @router.post("/")
# # def record_payment(
# #     payment: schemas.PaymentCreate,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Record a new payment"""
# #     try:
# #         db_payment = crud.create_payment(db, payment=payment)
# #         return db_payment
# #     except Exception as e:
# #         raise HTTPException(status_code=400, detail=str(e))


# # @router.get("/history/{tenant_id}")
# # def get_payment_history(
# #     tenant_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get payment history for tenant"""
# #     try:
# #         history = crud.get_payment_history(db, tenant_id=tenant_id)
# #         return history
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=str(e))


# # @router.get("/{payment_id}")
# # def get_payment(
# #     payment_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get payment by ID"""
# #     payment = crud.get_payment_by_id(db, payment_id=payment_id)
# #     if not payment:
# #         raise HTTPException(status_code=404, detail="Payment not found")
# #     return payment


# # @router.get("/{payment_id}/download-pdf")
# # async def download_receipt_pdf(
# #     payment_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Download receipt as PDF"""
# #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# #     if not payment:
# #         raise HTTPException(status_code=404, detail="Payment not found")
    
# #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# #     room = None
# #     property_obj = None
# #     if rent_cycle:
# #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
# #         if room:
# #             property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
# #             if not property_obj or property_obj.landlord_id != landlord.landlord_id:
# #                 raise HTTPException(status_code=403, detail="Not authorized")
    
# #     payment_data = {
# #         'receipt_number': payment.receipt_number,
# #         'tenant_name': tenant.full_name if tenant else "Unknown",
# #         'room_number': room.room_number if room else "N/A",
# #         'amount': payment.amount,
# #         'payment_date': payment.payment_date,
# #         'payment_method': payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
# #         'period_start': str(payment.period_start) if payment.period_start else "N/A",
# #         'period_end': str(payment.period_end) if payment.period_end else "N/A",
# #         'remaining_balance': tenant.balance if tenant else 0,
# #         'landlord_name': landlord.name,
# #         'landlord_contact': landlord.phone_number
# #     }
    
# #     try:
# #         from app.utils.pdf_generator import generate_payment_receipt
# #         pdf_buffer = generate_payment_receipt(payment_data)
        
# #         return StreamingResponse(
# #             pdf_buffer,
# #             media_type="application/pdf",
# #             headers={
# #                 "Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"
# #             }
# #         )
# #     except ImportError:
# #         raise HTTPException(status_code=500, detail="PDF library not installed. Run: pip install reportlab")
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


# # @router.post("/{payment_id}/share-whatsapp")
# # async def share_whatsapp(
# #     payment_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get WhatsApp share URL"""
# #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# #     if not payment:
# #         raise HTTPException(status_code=404, detail="Payment not found")
    
# #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# #     room = None
# #     if rent_cycle:
# #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
# #     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
# #     message = (
# #         f"*PAYMENT RECEIPT*\n\n"
# #         f"Receipt No: {payment.receipt_number}\n"
# #         f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
# #         f"Room: {room.room_number if room else 'N/A'}\n\n"
# #         f"Amount Paid: {int(payment.amount):,} FCFA\n"
# #         f"Payment Date: {payment_date_str}\n"
# #         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
# #         f"Period: {payment.period_start} to {payment.period_end}\n\n"
# #         f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n"
# #         f"Status: {'PAID IN FULL' if (tenant and tenant.balance == 0) else 'PARTIALLY PAID'}\n\n"
# #         f"Landlord: {landlord.name}\n"
# #         f"Contact: {landlord.phone_number}\n\n"
# #         f"Thank you!"
# #     )
    
# #     phone = tenant.phone_number if tenant else ""
# #     phone = ''.join(filter(str.isdigit, phone))
# #     if not phone.startswith('237'):
# #         phone = '237' + phone
    
# #     encoded_message = urllib.parse.quote(message)
# #     whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
# #     return {
# #         "success": True,
# #         "url": whatsapp_url,
# #         "phone": phone
# #     }


# # @router.post("/{payment_id}/share-email")
# # async def share_email(
# #     payment_id: int,
# #     db: Session = Depends(get_db),
# #     landlord = Depends(get_current_landlord)
# # ):
# #     """Get Email mailto URL"""
# #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# #     if not payment:
# #         raise HTTPException(status_code=404, detail="Payment not found")
    
# #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# #     room = None
# #     if rent_cycle:
# #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
# #     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
# #     subject = f"Payment Receipt - {payment.receipt_number}"
    
# #     body = (
# #         f"PAYMENT RECEIPT\n\n"
# #         f"Receipt No: {payment.receipt_number}\n"
# #         f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
# #         f"Room: {room.room_number if room else 'N/A'}\n\n"
# #         f"Amount Paid: {int(payment.amount):,} FCFA\n"
# #         f"Payment Date: {payment_date_str}\n"
# #         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
# #         f"Period: {payment.period_start} to {payment.period_end}\n\n"
# #         f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n\n"
# #         f"Landlord: {landlord.name}\n"
# #         f"Contact: {landlord.phone_number}"
# #     )
    
# #     email = tenant.email if tenant and tenant.email else ""
# #     encoded_subject = urllib.parse.quote(subject)
# #     encoded_body = urllib.parse.quote(body)
    
# #     mailto_url = f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
    
# #     return {
# #         "success": True,
# #         "url": mailto_url,
# #         "email": email
# #     }

















# # # # app/api/routers/payments.py - COMPLETE VERSION WITH PDF & WHATSAPP
# # # from fastapi import APIRouter, Depends, HTTPException
# # # from fastapi.responses import StreamingResponse
# # # from sqlalchemy.orm import Session
# # # from app import crud, schemas
# # # from app.database import get_db
# # # from app.utils.auth import get_current_landlord
# # # from app.models import Payment, RentCycle, Tenant, Room, Property
# # # import urllib.parse
# # # from datetime import datetime

# # # router = APIRouter(prefix="/payments", tags=["payments"])


# # # @router.post("/")
# # # def record_payment(
# # #     payment: schemas.PaymentCreate,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Record a new payment"""
# # #     try:
# # #         db_payment = crud.create_payment(db, payment=payment)
# # #         return db_payment
# # #     except Exception as e:
# # #         raise HTTPException(status_code=400, detail=str(e))


# # # @router.get("/history/{tenant_id}")
# # # def get_payment_history(
# # #     tenant_id: int,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Get payment history for a specific tenant"""
# # #     try:
# # #         history = crud.get_payment_history(db, tenant_id=tenant_id)
# # #         return history
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=str(e))


# # # @router.get("/{payment_id}")
# # # def get_payment(
# # #     payment_id: int,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Get a specific payment by ID"""
# # #     payment = crud.get_payment_by_id(db, payment_id=payment_id)
# # #     if not payment:
# # #         raise HTTPException(status_code=404, detail="Payment not found")
# # #     return payment


# # # @router.get("/{payment_id}/download-pdf")
# # # def download_receipt_pdf(
# # #     payment_id: int,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Download payment receipt as PDF"""
# # #     # Get payment
# # #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# # #     if not payment:
# # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # #     # Get related data
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# # #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# # #     room = None
# # #     property_obj = None
# # #     if rent_cycle:
# # #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
# # #         if room:
# # #             property_obj = db.query(Property).filter(Property.property_id == room.property_id).first()
# # #             # Verify landlord owns this
# # #             if not property_obj or property_obj.landlord_id != landlord.landlord_id:
# # #                 raise HTTPException(status_code=403, detail="Not authorized")
    
# # #     # Prepare data
# # #     payment_data = {
# # #         'receipt_number': payment.receipt_number,
# # #         'tenant_name': tenant.full_name if tenant else "Unknown",
# # #         'room_number': room.room_number if room else "N/A",
# # #         'amount': payment.amount,
# # #         'payment_date': payment.payment_date,
# # #         'payment_method': payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
# # #         'period_start': str(payment.period_start) if payment.period_start else "N/A",
# # #         'period_end': str(payment.period_end) if payment.period_end else "N/A",
# # #         'remaining_balance': tenant.balance if tenant else 0,
# # #         'landlord_name': landlord.name,
# # #         'landlord_contact': landlord.phone_number
# # #     }
    
# # #     try:
# # #         from app.utils.pdf_generator import generate_payment_receipt
# # #         pdf_buffer = generate_payment_receipt(payment_data)
        
# # #         return StreamingResponse(
# # #             pdf_buffer,
# # #             media_type="application/pdf",
# # #             headers={
# # #                 "Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"
# # #             }
# # #         )
# # #     except ImportError:
# # #         raise HTTPException(
# # #             status_code=500, 
# # #             detail="PDF generation not available. Install: pip install reportlab"
# # #         )
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"PDF error: {str(e)}")


# # # @router.post("/{payment_id}/share-whatsapp")
# # # def share_receipt_whatsapp(
# # #     payment_id: int,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Generate WhatsApp share link - returns URL for url_launcher"""
# # #     # Get payment
# # #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# # #     if not payment:
# # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# # #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# # #     room = None
# # #     if rent_cycle:
# # #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
# # #     # Format payment date
# # #     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
# # #     # Create message
# # #     message = (
# # #         f"*PAYMENT RECEIPT*\n\n"
# # #         f"Receipt No: {payment.receipt_number}\n"
# # #         f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
# # #         f"Room: {room.room_number if room else 'N/A'}\n\n"
# # #         f"Amount Paid: {int(payment.amount):,} FCFA\n"
# # #         f"Payment Date: {payment_date_str}\n"
# # #         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
# # #         f"Period: {payment.period_start} to {payment.period_end}\n\n"
# # #         f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n"
# # #         f"Status: {'PAID IN FULL' if (tenant and tenant.balance == 0) else 'PARTIALLY PAID'}\n\n"
# # #         f"Landlord: {landlord.name}\n"
# # #         f"Contact: {landlord.phone_number}\n\n"
# # #         f"Thank you for your payment!"
# # #     )
    
# # #     # Format phone for Cameroon
# # #     phone = tenant.phone_number if tenant else ""
# # #     phone = ''.join(filter(str.isdigit, phone))
    
# # #     # Add country code
# # #     if not phone.startswith('237'):
# # #         phone = '237' + phone
    
# # #     # Create WhatsApp URL
# # #     encoded_message = urllib.parse.quote(message)
# # #     whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
# # #     return {
# # #         "success": True,
# # #         "medium": "whatsapp",
# # #         "url": whatsapp_url,
# # #         "message": "WhatsApp link generated",
# # #         "phone": phone,
# # #         "preview_text": message[:100] + "..."
# # #     }


# # # @router.post("/{payment_id}/share-email")
# # # def share_receipt_email(
# # #     payment_id: int,
# # #     db: Session = Depends(get_db),
# # #     landlord = Depends(get_current_landlord)
# # # ):
# # #     """Generate Email mailto link"""
# # #     # Get payment
# # #     payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
# # #     if not payment:
# # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# # #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    
# # #     room = None
# # #     if rent_cycle:
# # #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    
# # #     # Format payment date
# # #     payment_date_str = payment.payment_date.strftime('%d/%m/%Y') if isinstance(payment.payment_date, datetime) else str(payment.payment_date)
    
# # #     # Subject and body
# # #     subject = f"Payment Receipt - {payment.receipt_number}"
    
# # #     body = (
# # #         f"PAYMENT RECEIPT\n\n"
# # #         f"Receipt No: {payment.receipt_number}\n"
# # #         f"Tenant: {tenant.full_name if tenant else 'Unknown'}\n"
# # #         f"Room: {room.room_number if room else 'N/A'}\n\n"
# # #         f"Amount Paid: {int(payment.amount):,} FCFA\n"
# # #         f"Payment Date: {payment_date_str}\n"
# # #         f"Payment Method: {payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method)}\n"
# # #         f"Period: {payment.period_start} to {payment.period_end}\n\n"
# # #         f"Remaining Balance: {int(tenant.balance if tenant else 0):,} FCFA\n"
# # #         f"Status: {'PAID IN FULL' if (tenant and tenant.balance == 0) else 'PARTIALLY PAID'}\n\n"
# # #         f"Landlord: {landlord.name}\n"
# # #         f"Contact: {landlord.phone_number}\n\n"
# # #         f"Thank you for your payment!"
# # #     )
    
# # #     # Create mailto URL
# # #     email = tenant.email if tenant and tenant.email else ""
# # #     encoded_subject = urllib.parse.quote(subject)
# # #     encoded_body = urllib.parse.quote(body)
    
# # #     mailto_url = f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
    
# # #     return {
# # #         "success": True,
# # #         "medium": "email",
# # #         "url": mailto_url,
# # #         "message": "Email link generated",
# # #         "email": email,
# # #         "preview_text": subject
# # #     }












# # # # # app/api/routers/payments.py - FIXED RESPONSE
# # # # from fastapi import APIRouter, Depends, HTTPException
# # # # from sqlalchemy.orm import Session
# # # # from typing import List
# # # # from app import crud, schemas
# # # # from app.database import get_db
# # # # from app.utils.auth import get_current_landlord

# # # # router = APIRouter(prefix="/payments", tags=["payments"])


# # # # @router.post("/")
# # # # def record_payment(
# # # #     payment: schemas.PaymentCreate,
# # # #     db: Session = Depends(get_db),
# # # #     landlord = Depends(get_current_landlord)
# # # # ):
# # # #     """Record a new payment"""
# # # #     try:
# # # #         db_payment = crud.create_payment(db, payment=payment)
# # # #         return db_payment
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=400, detail=str(e))


# # # # @router.get("/history/{tenant_id}")
# # # # def get_payment_history(
# # # #     tenant_id: int,
# # # #     db: Session = Depends(get_db),
# # # #     landlord = Depends(get_current_landlord)
# # # # ):
# # # #     """Get payment history for a specific tenant - NO RESPONSE MODEL"""
# # # #     try:
# # # #         history = crud.get_payment_history(db, tenant_id=tenant_id)
# # # #         return history
# # # #     except Exception as e:
# # # #         raise HTTPException(status_code=500, detail=str(e))


# # # # @router.get("/{payment_id}")
# # # # def get_payment(
# # # #     payment_id: int,
# # # #     db: Session = Depends(get_db),
# # # #     landlord = Depends(get_current_landlord)
# # # # ):
# # # #     """Get a specific payment by ID"""
# # # #     payment = crud.get_payment_by_id(db, payment_id=payment_id)
# # # #     if not payment:
# # # #         raise HTTPException(status_code=404, detail="Payment not found")
# # # #     return payment





# # # # # # app/api/routers/payments.py - ENHANCED VERSION
# # # # # from fastapi import APIRouter, Depends, HTTPException
# # # # # from fastapi.responses import StreamingResponse
# # # # # from sqlalchemy.orm import Session, joinedload
# # # # # from ... import schemas, crud, models
# # # # # from ...database import get_db
# # # # # from ...utils.auth import get_current_landlord_id
# # # # # from ...utils.pdf_generator import generate_payment_receipt
# # # # # from datetime import datetime

# # # # # router = APIRouter(prefix="/payments", tags=["Payments"])


# # # # # @router.post("/", response_model=schemas.PaymentResponse)
# # # # # def create_payment(
# # # # #     payment: schemas.PaymentCreate,
# # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """Record a new payment"""
# # # # #     rent_cycle = db.query(models.RentCycle).filter(
# # # # #         models.RentCycle.rent_cycle_id == payment.rent_cycle_id
# # # # #     ).first()
# # # # #     if not rent_cycle:
# # # # #         raise HTTPException(status_code=404, detail="Rent cycle not found")
    
# # # # #     room = db.query(models.Room).filter(
# # # # #         models.Room.room_id == rent_cycle.room_id
# # # # #     ).first()
# # # # #     if not room or room.property.landlord_id != landlord_id:
# # # # #         raise HTTPException(status_code=403, detail="Not authorized")
    
# # # # #     if payment.tenant_id != rent_cycle.tenant_id:
# # # # #         raise HTTPException(status_code=400, detail="Tenant not assigned to this rent cycle")
    
# # # # #     db_payment = crud.create_payment(db, payment)
# # # # #     if not db_payment:
# # # # #         raise HTTPException(status_code=404, detail="Payment creation failed")
    
# # # # #     return db_payment


# # # # # @router.get("/history/{tenant_id}", response_model=schemas.PaymentHistoryResponse)
# # # # # def get_payment_history(
# # # # #     tenant_id: int,
# # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # #     db: Session = Depends(get_db),
# # # # #     skip: int = 0,
# # # # #     limit: int = 100
# # # # # ):
# # # # #     """Get payment history for a tenant"""
# # # # #     tenant = db.query(models.Tenant).filter(
# # # # #         models.Tenant.tenant_id == tenant_id,
# # # # #         models.Tenant.is_active == True
# # # # #     ).first()
# # # # #     if not tenant:
# # # # #         raise HTTPException(status_code=404, detail="Tenant not found")
    
# # # # #     if tenant.assigned_room:
# # # # #         room = db.query(models.Room).filter(
# # # # #             models.Room.room_id == tenant.assigned_room_id
# # # # #         ).first()
# # # # #         if room.property.landlord_id != landlord_id:
# # # # #             raise HTTPException(status_code=403, detail="Not authorized")
    
# # # # #     payments = crud.get_payment_history(db, tenant_id, skip, limit)
# # # # #     return {"payments": payments}


# # # # # @router.get("/{payment_id}/pdf")
# # # # # def download_receipt_pdf(
# # # # #     payment_id: int,
# # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """
# # # # #     Download payment receipt as PDF
# # # # #     Uses ReportLab for professional receipt generation
# # # # #     """
# # # # #     # Get payment with all related data
# # # # #     payment = db.query(models.Payment).options(
# # # # #         joinedload(models.Payment.tenant),
# # # # #         joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
# # # # #     ).join(
# # # # #         models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
# # # # #     ).join(
# # # # #         models.Room, models.RentCycle.room_id == models.Room.room_id
# # # # #     ).join(
# # # # #         models.Property, models.Room.property_id == models.Property.property_id
# # # # #     ).filter(
# # # # #         models.Payment.payment_id == payment_id,
# # # # #         models.Property.landlord_id == landlord_id
# # # # #     ).first()
    
# # # # #     if not payment:
# # # # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # # # #     # Prepare payment data
# # # # #     payment_data = {
# # # # #         'receipt_number': payment.receipt_number,
# # # # #         'tenant_name': payment.tenant.full_name,
# # # # #         'room_number': payment.rent_cycle.room.room_number,
# # # # #         'amount': payment.amount,
# # # # #         'payment_date': payment.payment_date,
# # # # #         'payment_method': payment.payment_method.value,
# # # # #         'period_start': payment.period_start,
# # # # #         'period_end': payment.period_end,
# # # # #         'remaining_balance': payment.tenant.balance,
# # # # #         'landlord_name': payment.rent_cycle.room.property.landlord.name,
# # # # #         'landlord_contact': payment.rent_cycle.room.property.landlord.phone_number
# # # # #     }
    
# # # # #     # Generate PDF
# # # # #     pdf_buffer = generate_payment_receipt(payment_data)
    
# # # # #     # Return as streaming response
# # # # #     return StreamingResponse(
# # # # #         pdf_buffer,
# # # # #         media_type="application/pdf",
# # # # #         headers={
# # # # #             "Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"
# # # # #         }
# # # # #     )


# # # # # @router.post("/{payment_id}/share")
# # # # # def share_receipt(
# # # # #     payment_id: int,
# # # # #     medium: str,
# # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # #     db: Session = Depends(get_db)
# # # # # ):
# # # # #     """
# # # # #     Share receipt via WhatsApp or Email
# # # # #     Returns a URL that can be used with url_launcher in Flutter
# # # # #     """
# # # # #     payment = db.query(models.Payment).options(
# # # # #         joinedload(models.Payment.tenant),
# # # # #         joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
# # # # #     ).join(
# # # # #         models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
# # # # #     ).join(
# # # # #         models.Room, models.RentCycle.room_id == models.Room.room_id
# # # # #     ).join(
# # # # #         models.Property, models.Room.property_id == models.Property.property_id
# # # # #     ).filter(
# # # # #         models.Payment.payment_id == payment_id,
# # # # #         models.Property.landlord_id == landlord_id
# # # # #     ).first()
    
# # # # #     if not payment:
# # # # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # # # #     # Create receipt message
# # # # #     message = (
# # # # #         f"*PAYMENT RECEIPT*\n\n"
# # # # #         f"Receipt No: {payment.receipt_number}\n"
# # # # #         f"Tenant: {payment.tenant.full_name}\n"
# # # # #         f"Room: {payment.rent_cycle.room.room_number}\n\n"
# # # # #         f"Amount Paid: {int(payment.amount):,} FCFA\n"
# # # # #         f"Payment Date: {payment.payment_date.strftime('%d/%m/%Y')}\n"
# # # # #         f"Payment Method: {payment.payment_method.value}\n"
# # # # #         f"Period: {payment.period_start} to {payment.period_end}\n\n"
# # # # #         f"Remaining Balance: {int(payment.tenant.balance):,} FCFA\n"
# # # # #         f"Status: {'PAID IN FULL' if payment.tenant.balance == 0 else 'PARTIALLY PAID'}\n\n"
# # # # #         f"Landlord: {payment.rent_cycle.room.property.landlord.name}\n"
# # # # #         f"Contact: {payment.rent_cycle.room.property.landlord.phone_number}\n\n"
# # # # #         f"Thank you for your payment!"
# # # # #     )
    
# # # # #     # Generate share URL based on medium
# # # # #     if medium.lower() == 'whatsapp':
# # # # #         # Format phone number for WhatsApp (Cameroon format)
# # # # #         phone = payment.tenant.phone_number
# # # # #         # Remove spaces and special characters
# # # # #         phone = ''.join(filter(str.isdigit, phone))
# # # # #         # Add country code if not present
# # # # #         if not phone.startswith('237'):
# # # # #             phone = '237' + phone
        
# # # # #         # Create WhatsApp URL
# # # # #         import urllib.parse
# # # # #         encoded_message = urllib.parse.quote(message)
# # # # #         whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
        
# # # # #         return {
# # # # #             "success": True,
# # # # #             "medium": "whatsapp",
# # # # #             "url": whatsapp_url,
# # # # #             "message": "WhatsApp share link generated"
# # # # #         }
    
# # # # #     elif medium.lower() == 'email':
# # # # #         # Create email URL
# # # # #         import urllib.parse
# # # # #         subject = f"Payment Receipt - {payment.receipt_number}"
# # # # #         encoded_subject = urllib.parse.quote(subject)
# # # # #         encoded_body = urllib.parse.quote(message)
# # # # #         email = payment.tenant.email or ""
        
# # # # #         email_url = f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
        
# # # # #         return {
# # # # #             "success": True,
# # # # #             "medium": "email",
# # # # #             "url": email_url,
# # # # #             "message": "Email share link generated"
# # # # #         }
    
# # # # #     else:
# # # # #         raise HTTPException(status_code=400, detail="Invalid medium. Use 'whatsapp' or 'email'")







# # # # # # from fastapi import APIRouter, Depends, HTTPException
# # # # # # from fastapi.responses import StreamingResponse
# # # # # # from sqlalchemy.orm import Session, joinedload
# # # # # # from ... import schemas, crud, models
# # # # # # from ...database import get_db
# # # # # # from ...utils.auth import get_current_landlord_id
# # # # # # from reportlab.lib.pagesizes import letter
# # # # # # from reportlab.pdfgen import canvas
# # # # # # from io import BytesIO
# # # # # # from datetime import datetime

# # # # # # router = APIRouter(prefix="/payments", tags=["Payments"])

# # # # # # @router.post("/", response_model=schemas.PaymentResponse)
# # # # # # def create_payment(
# # # # # #     payment: schemas.PaymentCreate,
# # # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # # #     db: Session = Depends(get_db)
# # # # # # ):
# # # # # #     rent_cycle = db.query(models.RentCycle).filter(
# # # # # #         models.RentCycle.rent_cycle_id == payment.rent_cycle_id
# # # # # #     ).first()
# # # # # #     if not rent_cycle:
# # # # # #         raise HTTPException(status_code=404, detail="Rent cycle not found")
# # # # # #     room = db.query(models.Room).filter(
# # # # # #         models.Room.room_id == rent_cycle.room_id
# # # # # #     ).first()
# # # # # #     if not room or room.property.landlord_id != landlord_id:
# # # # # #         raise HTTPException(status_code=403, detail="Not authorized")
# # # # # #     if payment.tenant_id != rent_cycle.tenant_id:
# # # # # #         raise HTTPException(status_code=400, detail="Tenant not assigned to this rent cycle")
    
# # # # # #     db_payment = crud.create_payment(db, payment)
# # # # # #     if not db_payment:
# # # # # #         raise HTTPException(status_code=404, detail="Payment creation failed")
# # # # # #     return db_payment

# # # # # # @router.get("/history/{tenant_id}", response_model=schemas.PaymentHistoryResponse)
# # # # # # def get_payment_history(
# # # # # #     tenant_id: int,
# # # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # # #     db: Session = Depends(get_db),
# # # # # #     skip: int = 0,
# # # # # #     limit: int = 100
# # # # # # ):
# # # # # #     tenant = db.query(models.Tenant).filter(
# # # # # #         models.Tenant.tenant_id == tenant_id,
# # # # # #         models.Tenant.is_active == True
# # # # # #     ).first()
# # # # # #     if not tenant:
# # # # # #         raise HTTPException(status_code=404, detail="Tenant not found")
# # # # # #     if tenant.assigned_room:
# # # # # #         room = db.query(models.Room).filter(
# # # # # #             models.Room.room_id == tenant.assigned_room_id
# # # # # #         ).first()
# # # # # #         if room.property.landlord_id != landlord_id:
# # # # # #             raise HTTPException(status_code=403, detail="Not authorized")
    
# # # # # #     payments = crud.get_payment_history(db, tenant_id, skip, limit)
# # # # # #     return {"payments": payments}

# # # # # # @router.get("/{payment_id}/pdf")
# # # # # # def download_receipt_pdf(
# # # # # #     payment_id: int,
# # # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # # #     db: Session = Depends(get_db)
# # # # # # ):
# # # # # #     payment = db.query(models.Payment).options(
# # # # # #         joinedload(models.Payment.tenant),
# # # # # #         joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
# # # # # #     ).join(
# # # # # #         models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
# # # # # #     ).join(
# # # # # #         models.Room, models.RentCycle.room_id == models.Room.room_id
# # # # # #     ).join(
# # # # # #         models.Property, models.Room.property_id == models.Property.property_id
# # # # # #     ).filter(
# # # # # #         models.Payment.payment_id == payment_id,
# # # # # #         models.Property.landlord_id == landlord_id
# # # # # #     ).first()
# # # # # #     if not payment:
# # # # # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # # # # #     buffer = BytesIO()
# # # # # #     p = canvas.Canvas(buffer, pagesize=letter)
# # # # # #     p.drawString(100, 750, f"Receipt: {payment.receipt_number}")
# # # # # #     p.drawString(100, 730, f"Tenant: {payment.tenant.full_name}")
# # # # # #     p.drawString(100, 710, f"Room: {payment.rent_cycle.room.room_number}")
# # # # # #     p.drawString(100, 690, f"Amount Paid: {payment.amount}")
# # # # # #     p.drawString(100, 670, f"Payment Date: {payment.payment_date.strftime('%Y-%m-%d')}")
# # # # # #     p.drawString(100, 650, f"Period: {payment.period_start} to {payment.period_end}")
# # # # # #     p.drawString(100, 630, f"Remaining Balance: {payment.tenant.balance}")
# # # # # #     p.drawString(100, 610, f"Landlord: {payment.rent_cycle.room.property.landlord.name}")
# # # # # #     p.drawString(100, 590, f"Contact: {payment.rent_cycle.room.property.landlord.phone_number}")
# # # # # #     p.showPage()
# # # # # #     p.save()
# # # # # #     buffer.seek(0)
# # # # # #     return StreamingResponse(
# # # # # #         buffer,
# # # # # #         media_type="application/pdf",
# # # # # #         headers={"Content-Disposition": f"attachment; filename=receipt_{payment.receipt_number}.pdf"}
# # # # # #     )

# # # # # # @router.post("/{payment_id}/share")
# # # # # # def share_receipt(
# # # # # #     payment_id: int,
# # # # # #     medium: str,
# # # # # #     landlord_id: int = Depends(get_current_landlord_id),
# # # # # #     db: Session = Depends(get_db)
# # # # # # ):
# # # # # #     payment = db.query(models.Payment).options(
# # # # # #         joinedload(models.Payment.tenant),
# # # # # #         joinedload(models.Payment.rent_cycle).joinedload(models.RentCycle.room).joinedload(models.Room.property).joinedload(models.Property.landlord)
# # # # # #     ).join(
# # # # # #         models.RentCycle, models.Payment.rent_cycle_id == models.RentCycle.rent_cycle_id
# # # # # #     ).join(
# # # # # #         models.Room, models.RentCycle.room_id == models.Room.room_id
# # # # # #     ).join(
# # # # # #         models.Property, models.Room.property_id == models.Property.property_id
# # # # # #     ).filter(
# # # # # #         models.Payment.payment_id == payment_id,
# # # # # #         models.Property.landlord_id == landlord_id
# # # # # #     ).first()
# # # # # #     if not payment:
# # # # # #         raise HTTPException(status_code=404, detail="Payment not found")
    
# # # # # #     message = (
# # # # # #         f"Receipt: {payment.receipt_number}\n"
# # # # # #         f"Tenant: {payment.tenant.full_name}\n"
# # # # # #         f"Room: {payment.rent_cycle.room.room_number}\n"
# # # # # #         f"Amount Paid: {payment.amount}\n"
# # # # # #         f"Payment Date: {payment.payment_date.strftime('%Y-%m-%d')}\n"
# # # # # #         f"Period: {payment.period_start} to {payment.period_end}\n"
# # # # # #         f"Remaining Balance: {payment.tenant.balance}\n"
# # # # # #         f"Landlord: {payment.rent_cycle.room.property.landlord.name}\n"
# # # # # #         f"Contact: {payment.rent_cycle.room.property.landlord.phone_number}"
# # # # # #     )
# # # # # #     crud.create_reminder(db, payment.tenant_id, message, medium)
# # # # # #     return {"message": f"Receipt shared via {medium}"}






