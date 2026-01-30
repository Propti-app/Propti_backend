# # app/crud/payment.py
# from sqlalchemy.orm import Session
# from sqlalchemy import func, and_
# from app.models import Payment, RentCycle, Tenant, Room, Property
# from app.schemas import PaymentCreate
# from datetime import datetime

# def create_payment(db: Session, payment: PaymentCreate):
#     """Create a new payment and update tenant balance"""
#     # Get the tenant and validate
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
#     if not tenant:
#         raise ValueError("Tenant not found")
    
#     # Get active rent cycle
#     rent_cycle = db.query(RentCycle).filter(
#         RentCycle.room_id == tenant.assigned_room_id,
#         RentCycle.is_active == True
#     ).first()
    
#     if not rent_cycle:
#         raise ValueError("No active rent cycle found for this tenant's room")
    
#     # Create payment
#     db_payment = Payment(
#         tenant_id=payment.tenant_id,
# #         rent_cycle_id=rent_cycle.rent_cycle_id,
# #         amount=payment.amount,
# #         payment_method=payment.payment_method,
# #         payment_date=payment.payment_date or datetime.now(),
# #         notes=payment.notes
# #     )
    
# #     db.add(db_payment)
    
# #     # Update tenant balance
# #     tenant.balance = max(0, tenant.balance - payment.amount)
    
# #     db.commit()
# #     db.refresh(db_payment)
    
# #     return db_payment


# def get_payment_history(db: Session, tenant_id: int, skip: int = 0, limit: int = 50):
#     """Get payment history for a tenant with proper joins"""
#     payments = db.query(Payment).join(
#         RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
#     ).join(
#         Room, RentCycle.room_id == Room.room_id
#     ).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Payment.tenant_id == tenant_id
#     ).order_by(
#         Payment.payment_date.desc()
#     ).offset(skip).limit(limit).all()
    
#     return payments


# def get_payment_by_id(db: Session, payment_id: int):
#     """Get a specific payment by ID"""
#     return db.query(Payment).filter(Payment.payment_id == payment_id).first()


# def get_landlord_payments(db: Session, landlord_id: int, skip: int = 0, limit: int = 100):
#     """Get all payments for a landlord's properties"""
#     payments = db.query(Payment).join(
#         Tenant, Payment.tenant_id == Tenant.tenant_id
#     ).join(
#         Room, Tenant.assigned_room_id == Room.room_id
#     ).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Property.landlord_id == landlord_id
#     ).order_by(
#         Payment.payment_date.desc()
#     ).offset(skip).limit(limit).all()
    
#     return payments


# def get_total_payments_for_period(db: Session, landlord_id: int, start_date=None, end_date=None):
#     """Calculate total payments for a landlord in a given period"""
#     query = db.query(func.sum(Payment.amount)).join(
#         Tenant, Payment.tenant_id == Tenant.tenant_id
#     ).join(
#         Room, Tenant.assigned_room_id == Room.room_id
#     ).join(
#         Property, Room.property_id == Property.property_id
#     ).filter(
#         Property.landlord_id == landlord_id
#     )
    
#     if start_date:
#         query = query.filter(Payment.payment_date >= start_date)
#     if end_date:
#         query = query.filter(Payment.payment_date <= end_date)
    
#     total = query.scalar()
#     return total or 0.0




from sqlalchemy.orm import Session
from ..models import Payment, PaymentStatus, Tenant, Room, RentCycle, Landlord
from ..schemas import PaymentCreate
import uuid
from sqlalchemy.sql import func

def create_payment(db: Session, payment: PaymentCreate):
    # Verify related entities
    tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
    rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
    if not tenant or not rent_cycle:
        return None
    room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
    landlord = db.query(Landlord).filter(Landlord.landlord_id == room.property.landlord_id).first()
    if not room or not landlord:
        return None
    
    # Calculate total payments for this rent cycle
    total_paid = db.query(func.sum(Payment.amount)).filter(
        Payment.rent_cycle_id == payment.rent_cycle_id,
        Payment.tenant_id == payment.tenant_id
    ).scalar() or 0.0

    # Initialize or update tenant balance
    tenant.balance = rent_cycle.amount - total_paid
    if tenant.balance < 0:
        tenant.balance = 0  # Prevent negative balance (unless overpayments allowed)

    # Create payment
    db_payment = Payment(
        rent_cycle_id=payment.rent_cycle_id,
        tenant_id=payment.tenant_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        period_start=payment.period_start,
        period_end=payment.period_end,
        receipt_number=f"REC-{uuid.uuid4().hex[:8].upper()}"
    )
    db.add(db_payment)

    # Update balance with new payment
    tenant.balance = max(0, tenant.balance - payment.amount)

    # Update payment status
    payment_status = (
        PaymentStatus.PAID if tenant.balance == 0
        else PaymentStatus.PARTIAL if tenant.balance < rent_cycle.amount
        else PaymentStatus.OVERDUE
    )
    rent_cycle.payment_status = payment_status
    room.payment_status = payment_status

    db.commit()
    db.refresh(db_payment)

    return {
        "payment_id": db_payment.payment_id,
        "rent_cycle_id": db_payment.rent_cycle_id,
        "tenant_id": db_payment.tenant_id,
        "amount": db_payment.amount,
        "payment_date": db_payment.payment_date,
        "payment_method": db_payment.payment_method,
        "period_start": db_payment.period_start,
        "period_end": db_payment.period_end,
        "receipt_number": db_payment.receipt_number,
        "created_at": db_payment.created_at,
        "tenant_name": tenant.full_name,
        "room_number": room.room_number,
        "landlord_name": landlord.name,
        "landlord_contact": landlord.phone_number,
        "remaining_balance": tenant.balance
    }

def get_payment_history(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    payments = db.query(Payment).join(
        Tenant, Payment.tenant_id == Tenant.tenant_id
    ).join(
        RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
    ).join(
        Room, RentCycle.room_id == Room.room_id
    ).join(
        Landlord, Room.property.landlord_id == Landlord.landlord_id
    ).filter(
        Payment.tenant_id == tenant_id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "payment_id": p.payment_id,
            "rent_cycle_id": p.rent_cycle_id,
            "tenant_id": p.tenant_id,
            "amount": p.amount,
            "payment_date": p.payment_date,
            "payment_method": p.payment_method,
            "period_start": p.period_start,
            "period_end": p.period_end,
            "receipt_number": p.receipt_number,
            "created_at": p.created_at,
            "tenant_name": p.tenant.full_name,
            "room_number": p.rent_cycle.room.room_number,
            "landlord_name": p.rent_cycle.room.property.landlord.name,
            "landlord_contact": p.rent_cycle.room.property.landlord.phone_number,
            "remaining_balance": p.tenant.balance
        } for p in payments
    ]






# from sqlalchemy.orm import Session
# from ..models import Payment, PaymentStatus, Tenant, Room, RentCycle, Landlord
# from ..schemas import PaymentCreate
# import uuid

# def create_payment(db: Session, payment: PaymentCreate):
#     # Verify related entities
#     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
#     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
#     if not tenant or not rent_cycle:
#         return None
#     room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
#     landlord = db.query(Landlord).filter(Landlord.landlord_id == room.property.landlord_id).first()
#     if not room or not landlord:
#         return None
    
#     # Initialize tenant balance if null or reset for new rent cycle
#     if tenant.balance is None or tenant.balance > rent_cycle.amount:
#         tenant.balance = rent_cycle.amount  # Set balance to rent cycle amount (e.g., 400000)

#     # Create payment
#     db_payment = Payment(
#         rent_cycle_id=payment.rent_cycle_id,
#         tenant_id=payment.tenant_id,
#         amount=payment.amount,
#         payment_method=payment.payment_method,
#         period_start=payment.period_start,
#         period_end=payment.period_end,
#         receipt_number=f"REC-{uuid.uuid4().hex[:8].upper()}"
#     )
#     db.add(db_payment)

#     # Update tenant balance (subtract payment, prevent negative balance)
#     tenant.balance = max(0, tenant.balance - payment.amount)

#     # Update payment status
#     payment_status = (
#         PaymentStatus.PAID if tenant.balance == 0
#         else PaymentStatus.PARTIAL if tenant.balance < rent_cycle.amount
#         else PaymentStatus.OVERDUE
#     )
#     rent_cycle.payment_status = payment_status
#     room.payment_status = payment_status

#     db.commit()
#     db.refresh(db_payment)

#     return {
#         "payment_id": db_payment.payment_id,
#         "rent_cycle_id": db_payment.rent_cycle_id,
#         "tenant_id": db_payment.tenant_id,
#         "amount": db_payment.amount,
#         "payment_date": db_payment.payment_date,
#         "payment_method": db_payment.payment_method,
#         "period_start": db_payment.period_start,
#         "period_end": db_payment.period_end,
#         "receipt_number": db_payment.receipt_number,
#         "created_at": db_payment.created_at,
#         "tenant_name": tenant.full_name,
#         "room_number": room.room_number,
#         "landlord_name": landlord.name,
#         "landlord_contact": landlord.phone_number,
#         "remaining_balance": tenant.balance
#     }

# def get_payment_history(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
#     payments = db.query(Payment).join(
#         Tenant, Payment.tenant_id == Tenant.tenant_id
#     ).join(
#         RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
#     ).join(
#         Room, RentCycle.room_id == Room.room_id
#     ).join(
#         Landlord, Room.property.landlord_id == Landlord.landlord_id
#     ).filter(
#         Payment.tenant_id == tenant_id
#     ).offset(skip).limit(limit).all()
    
#     return [
#         {
#             "payment_id": p.payment_id,
#             "rent_cycle_id": p.rent_cycle_id,
#             "tenant_id": p.tenant_id,
#             "amount": p.amount,
#             "payment_date": p.payment_date,
#             "payment_method": p.payment_method,
#             "period_start": p.period_start,
#             "period_end": p.period_end,
#             "receipt_number": p.receipt_number,
#             "created_at": p.created_at,
#             "tenant_name": p.tenant.full_name,
#             "room_number": p.rent_cycle.room.room_number,
#             "landlord_name": p.rent_cycle.room.property.landlord.name,
#             "landlord_contact": p.rent_cycle.room.property.landlord.phone_number,
#             "remaining_balance": p.tenant.balance
#         } for p in payments
#     ]




# # from sqlalchemy.orm import Session
# # from ..models import Payment, PaymentStatus, Tenant, Room, RentCycle, Landlord
# # from ..schemas import PaymentCreate
# # import uuid

# # def create_payment(db: Session, payment: PaymentCreate):
# #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
# #     room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
# #     landlord = db.query(Landlord).filter(Landlord.landlord_id == room.property.landlord_id).first()
    
# #     if not tenant or not rent_cycle or not room or not landlord:
# #         return None
    
# #     db_payment = Payment(
# #         rent_cycle_id=payment.rent_cycle_id,
# #         tenant_id=payment.tenant_id,
# #         amount=payment.amount,
# #         payment_method=payment.payment_method,
# #         period_start=payment.period_start,
# #         period_end=payment.period_end,
# #         receipt_number=f"REC-{uuid.uuid4().hex[:8].upper()}"
# #     )
# #     db.add(db_payment)
    
# #     tenant.balance -= payment.amount
# #     payment_status = (
# #         PaymentStatus.PAID if tenant.balance <= 0
# #         else PaymentStatus.PARTIAL if tenant.balance < rent_cycle.amount
# #         else PaymentStatus.OVERDUE
# #     )
# #     rent_cycle.payment_status = payment_status
# #     room.payment_status = payment_status
    
# #     db.commit()
# #     db.refresh(db_payment)
    
# #     return {
# #         "payment_id": db_payment.payment_id,
# #         "rent_cycle_id": db_payment.rent_cycle_id,
# #         "tenant_id": db_payment.tenant_id,
# #         "amount": db_payment.amount,
# #         "payment_date": db_payment.payment_date,
# #         "payment_method": db_payment.payment_method,
# #         "period_start": db_payment.period_start,
# #         "period_end": db_payment.period_end,
# #         "receipt_number": db_payment.receipt_number,
# #         "created_at": db_payment.created_at,
# #         "tenant_name": tenant.full_name,
# #         "room_number": room.room_number,
# #         "landlord_name": landlord.name,
# #         "landlord_contact": landlord.phone_number,
# #         "remaining_balance": tenant.balance
# #     }

# # def get_payment_history(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
# #     payments = db.query(Payment).join(
# #         Tenant, Payment.tenant_id == Tenant.tenant_id
# #     ).join(
# #         RentCycle, Payment.rent_cycle_id == RentCycle.rent_cycle_id
# #     ).join(
# #         Room, RentCycle.room_id == Room.room_id
# #     ).join(
# #         Landlord, Room.property.landlord_id == Landlord.landlord_id
# #     ).filter(
# #         Payment.tenant_id == tenant_id
# #     ).offset(skip).limit(limit).all()
    
# #     return [
# #         {
# #             "payment_id": p.payment_id,
# #             "rent_cycle_id": p.rent_cycle_id,
# #             "tenant_id": p.tenant_id,
# #             "amount": p.amount,
# #             "payment_date": p.payment_date,
# #             "payment_method": p.payment_method,
# #             "period_start": p.period_start,
# #             "period_end": p.period_end,
# #             "receipt_number": p.receipt_number,
# #             "created_at": p.created_at,
# #             "tenant_name": p.tenant.full_name,
# #             "room_number": p.rent_cycle.room.room_number,
# #             "landlord_name": p.rent_cycle.room.property.landlord.name,
# #             "landlord_contact": p.rent_cycle.room.property.landlord.phone_number,
# #             "remaining_balance": p.tenant.balance
# #         } for p in payments
# #     ]



















# # # from sqlalchemy.orm import Session
# # # from ..models import Payment, RentCycle, Room, Tenant
# # # from ..schemas import PaymentCreate
# # # import uuid

# # # def create_payment(db: Session, payment: PaymentCreate):
# # #     # Verify rent cycle and tenant
# # #     rent_cycle = db.query(RentCycle).filter(RentCycle.rent_cycle_id == payment.rent_cycle_id).first()
# # #     tenant = db.query(Tenant).filter(Tenant.tenant_id == payment.tenant_id).first()
# # #     if not rent_cycle or not tenant:
# # #         return None
# # #     # Generate unique receipt number
# # #     receipt_number = f"REC-{uuid.uuid4().hex[:8].upper()}"
# # #     db_payment = Payment(
# # #         rent_cycle_id=payment.rent_cycle_id,
# # #         tenant_id=payment.tenant_id,
# # #         amount=payment.amount,
# # #         receipt_number=receipt_number
# # #     )
# # #     db.add(db_payment)
# # #     # Update tenant balance
# # #     tenant.balance -= payment.amount
# # #     # Update rent cycle and room payment status
# # #     if tenant.balance <= 0:
# # #         rent_cycle.payment_status = "Paid"
# # #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
# # #         if room:
# # #             room.payment_status = "Paid"
# # #     elif tenant.balance < rent_cycle.amount:
# # #         rent_cycle.payment_status = "Partial"
# # #         room = db.query(Room).filter(Room.room_id == rent_cycle.room_id).first()
# # #         if room:
# # #             room.payment_status = "Partial"
# # #     db.commit()
# # #     db.refresh(db_payment)
# # #     return db_payment